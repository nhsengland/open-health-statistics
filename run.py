import urllib
import urllib.request
import json
import pandas as pd
from pandas import json_normalize
from datetime import datetime
import time
import plotly
import plotly.graph_objects as go


# Data collection

# GitHub 

# GitHub orgs
github_orgs = [
    "nhsx",
    "111Online",
    "NHSDigital",
    "nhsconnect",
    "nhsengland",
    "nhs-pycom",
    "nhs-r-community",
    "nhsuk",
    "publichealthengland",
]

# Get the GitHub data from the API
df_github = pd.DataFrame()
for org in github_orgs:
    data = [1]
    page = 1
    while bool(data) is True:
        url = (
            "https://api.github.com/orgs/"
            + str(org)
            + "/repos?page="
            + str(page)
            + "&per_page=100"
        )
        response = urllib.request.urlopen(url)
        data = json.loads(response.read())
        flat_data = json_normalize(data)
        df_github = df_github.append(flat_data)
        page = page + 1
        time.sleep(10)  # Avoid unauthenticated requests limit (10 per minute)

# GitLab

# GitLab group ids
gitlab_groups = [
    2955125 # NHSBSA
]

# Get the GitLab data from the API
df_gitlab = pd.DataFrame()
for group in gitlab_groups:
    data = [1]
    page = 1
    while bool(data) is True:
        url = (
            "https://gitlab.com/api/v4/groups/"
            + str(group)
            + "/projects?include_subgroups=true&page="
            + str(page)
            + "&per_page=100"
        )
        response = urllib.request.urlopen(url)
        data = json.loads(response.read())
        flat_data = json_normalize(data)
        df_gitlab = df_gitlab.append(flat_data)
        page = page + 1

# Unfortunately it is missing license + language data so we have an additional
# step to get this...

# GitLab project ids
gitlab_projects = list(df_gitlab['id'])

# Get the GitLab license + language data for each project
top_languages = []
licenses = []
for project in gitlab_projects:
    
    # Then get the license for each project
    url = (
        "https://gitlab.com/api/v4/projects/"
        + str(project)
        + "?license=true"
    )
    response = urllib.request.urlopen(url)
    license_dict = json.loads(response.read())['license']
    license_ = license_dict.get('name') if license_dict else None
    
    # Then get the top language for each project
    url = (
        "https://gitlab.com/api/v4/projects/"
        + str(project)
        + "/languages"
    )
    response = urllib.request.urlopen(url)
    languages = json.loads(response.read())
    top_language = max(languages, key = languages.get) if languages else None
        
    # Append the data 
    licenses.append(license_)
    top_languages.append(top_language)
    
# Add the extra columns to the GitLab df
df_gitlab['license'] = licenses
df_gitlab['top_language'] = top_languages

# Subset the path to get the group name
df_gitlab['org'] = df_gitlab['namespace.full_path'].apply(
    lambda x: x.split('/')[0]
)

# Create table

# GitHub aggregate
df_github_aggregate = (
    df_github
    .groupby(["owner.login"])
    .agg(
        open_repos = ("name", "count"),
        stargazers = ("stargazers_count", "sum"),
        forks = ("forks_count", "sum"),
        open_issues = ("open_issues_count", "sum"),
        top_license = ("license.name", lambda x: x.value_counts().index[0]),
        top_language = ("language", lambda x: x.value_counts().index[0]),
    )
    .rename_axis("org")
    .reset_index()
)

# GitLab aggregate
df_gitlab_aggregate = (
    df_gitlab
    .groupby(["org"])
    .agg(
        open_repos = ("name", "count"),
        stargazers = ("star_count", "sum"),
        forks = ("forks_count", "sum"),
        open_issues = ("open_issues_count", "sum"),
        top_license = ("license", lambda x: x.value_counts().index[0]),
        top_language = ("top_language", lambda x: x.value_counts().index[0]),
    )
    .reset_index()
)

# Combine GitHub and GitLab aggregate tables and sort by open repos
df_aggregate = (
    pd.concat([df_github_aggregate, df_gitlab_aggregate])
    .sort_values(by='open_repos', ascending=False)
    .reset_index(drop=True)
)

# Make the column names nice
df_aggregate.columns = [   
    "Org",
    "Open Repos",
    "Stargazers",
    "Forks",
    "Open Issues",
    "Top License",
    "Top Language"
]

# Write to file (.html)
df_html = df_aggregate.to_html(classes="summary", index=False)
with open("_includes/table.html", "w") as file:
    file.write(df_html)

# Create plot

# Github time series
df_github["date"] = pd.to_datetime(df_github["created_at"])
df_github_ts = (    
    df_github
    .groupby(['owner.login', pd.Grouper(key="date", freq="M")])
    .agg(total_open_repos = ("name", "count"))
    .groupby(level=[0])
    .cumsum()
    .rename_axis(index={"owner.login": "org"})
    .reset_index()
)

# GitLab time series
df_gitlab["date"] = pd.to_datetime(df_gitlab["created_at"])
df_gitlab_ts = (    
    df_gitlab
    .groupby(['org', pd.Grouper(key="date", freq="M")])
    .agg(total_open_repos = ("name", "count"))
    .groupby(level=[0])
    .cumsum()
    .reset_index()
)

# Combine GitHub and GitLab time series 
df_ts = pd.concat([df_github_ts, df_gitlab_ts]).reset_index(drop=True)

# Make the column names nice
df_ts.columns = [   
    "Org",
    "Date",
    "Total Open Repositories"
]

# Sort to the same order as the aggregate table
df_ts["Org"] = df_ts["Org"].astype("category")
df_ts["Org"].cat.set_categories(list(df_aggregate["Org"]), inplace=True)

# Initialise plot
fig = go.Figure()

# Loop over each org and add line to chart
for org, df_ts_ in df_ts.groupby('Org'):
    fig.add_traces(
        go.Scatter(
            x=df_ts_["Date"],
            y=df_ts_["Total Open Repositories"],
            mode="lines",
            name=org,
            line={'shape': 'hvh'},
            # TODO: # Add discrete colour sequence if needed
        )
    )
    
# Asthetics of the plot
fig.update_layout(
    {
        "plot_bgcolor": "rgba(0, 0, 0, 0)",
        "paper_bgcolor": "rgba(0, 0, 0, 0)",
    },
    autosize=True,
    hovermode='x'
)

# Add title and dynamic range selector to x axis
fig.update_xaxes(
    title_text='Date',
    rangeselector=dict(
        buttons=list(
            [
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all"),
            ]
        )
    )
)

# Add title to y axis
fig.update_yaxes(title_text='Total Open Repositories')
    
# Write out to file (.html)
config = {"displayModeBar": False, "displaylogo": False}
plot_div = plotly.offline.plot(
    fig, include_plotlyjs=False, output_type="div", config=config
)
with open("_includes/chart.html", "w") as file:
    file.write(plot_div)

# Collect update data

# Grab timestamp
data_updated = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

# Write out to file (.html)
html_str = (
    '<p><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16"><path fill-rule="evenodd" d="M1.5 8a6.5 6.5 0 1113 0 6.5 6.5 0 01-13 0zM8 0a8 8 0 100 16A8 8 0 008 0zm.5 4.75a.75.75 0 00-1.5 0v3.5a.75.75 0 00.471.696l2.5 1a.75.75 0 00.557-1.392L8.5 7.742V4.75z"></path></svg> Latest Data: '
    + data_updated
    + "</p>"
)
with open("_includes/update.html", "w") as file:
    file.write(html_str)