import urllib.request  # https://stackoverflow.com/a/41217363
import json
import pandas as pd
from datetime import datetime
import time
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots


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
    "CDU-data-science-team",
    "the-strategy-unit",
    "ebmdatalab",
    "opensafely",
    "HFAnalyticsLab",
    "nhs-bnssg-analytics"
]

# Get the GitHub data from the API (note we can only make 60 calls per hour so
# if we have over 60 orgs would have to try a different strategy)
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
        flat_data = pd.json_normalize(data)
        df_github = df_github.append(flat_data)
        page = page + 1

# Add a column of 1s to sum for open_repos (this enables us to use sum() on all
# columns later)
df_github["open_repos"] = 1

# Filter and rename columns
df_github = df_github[
    [
        "owner.login",
        "owner.html_url",
        "created_at",
        "open_repos",
        "stargazers_count",
        "forks_count",
        "open_issues_count",
        "license.name",
        "language",
    ]
].rename(
    columns={
        "owner.login": "org",
        "owner.html_url": "link",
        "created_at": "date",
        "stargazers_count": "stargazers",
        "forks_count": "forks",
        "open_issues_count": "open_issues",
        "license.name": "license",
    }
)

# GitLab

# GitLab group ids
gitlab_groups = [2955125]  # NHSBSA

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
        flat_data = pd.json_normalize(data)
        df_gitlab = df_gitlab.append(flat_data)
        page = page + 1
        time.sleep(0.2)  # Avoid unauthenticated requests limit (10 per sec)

# Subset the path to get the group name
df_gitlab["org"] = df_gitlab["namespace.full_path"].apply(lambda x: x.split("/")[0])

# Add the link
df_gitlab["link"] = "https://gitlab.com/" + df_gitlab["org"]

# Add a column of 1s to sum for open_repos (this enables us to use sum() on all
# columns later)
df_gitlab["open_repos"] = 1

# Unfortunately it is missing license + language data so we have an additional
# step to get this...

# GitLab project ids
gitlab_projects = list(df_gitlab["id"])

# Get the GitLab license + language data for each project
top_languages = []
licenses = []
for project in gitlab_projects:

    # Then get the license for each project
    url = "https://gitlab.com/api/v4/projects/" + str(project) + "?license=true"
    response = urllib.request.urlopen(url)
    license_dict = json.loads(response.read())["license"]
    license_ = license_dict.get("name") if license_dict else None

    # Then get the top language for each project
    url = "https://gitlab.com/api/v4/projects/" + str(project) + "/languages"
    response = urllib.request.urlopen(url)
    languages = json.loads(response.read())
    top_language = max(languages, key=languages.get) if languages else None

    # Append the data
    licenses.append(license_)
    top_languages.append(top_language)

# Add the extra columns to the GitLab df
df_gitlab["license"] = licenses
df_gitlab["language"] = top_languages

# Filter and rename columns
df_gitlab = df_gitlab[
    [
        "org",
        "link",
        "created_at",
        "open_repos",
        "star_count",
        "forks_count",
        "open_issues_count",
        "license",
        "language",
    ]
].rename(
    columns={
        "created_at": "date",
        "star_count": "stargazers",
        "forks_count": "forks",
        "open_issues_count": "open_issues",
    }
)

# Combine GitHub and GitLab tables
df_combined = pd.concat([df_github, df_gitlab]).reset_index(drop=True)

# Data processing

# Now we have a standardised table we can begin to split and aggregate... start
# by changing date to a date type (day only)
df_combined["date"] = pd.to_datetime(df_combined["date"]).apply(
    lambda x: x.strftime("%Y-%m-%d")
)

# Cumulative sum by org, link and date
df_combined_cumsum = (
    df_combined.groupby(["org", "link", "date"])
    .sum()
    .groupby(level=[0])
    .cumsum()
    .reset_index()
)

# Now we need to get the top license + language at each date for each
# organisation. This is not so straight forward.

# Loop over each org and grab the top license + language at each date
df_combined_cumsum_additional = pd.DataFrame()
for org, df in df_combined.groupby("org"):

    # Define the cols
    cols = ["license", "language"]

    # Convert the date and cols to categoricals (within their org). This
    # means when we group by them it will find all combinations (so we get a
    # result for a license even if it didn't increment at that date)
    cat_cols = ["date"] + cols
    df[cat_cols] = df[cat_cols].apply(lambda x: x.astype("category"))

    # Loop over each col
    additional_df_list = []
    for col in cols:

        # Get cumulative counts of each value for each org
        df_cumsum = (
            df.groupby(["date", col])
            .size()
            .groupby(level=[1])
            .cumsum()
            .to_frame("count")
            .reset_index()
        )

        # Now get the highest count each day
        df_cumsum_max = df_cumsum.groupby("date").max().reset_index()

        # Now inner join and ensure we only have one row per day
        df_top = (
            pd.merge(df_cumsum, df_cumsum_max)
            .drop_duplicates(["date", "count"])
            .drop(columns="count")
        )

        # Append it to the new list of dfs
        additional_df_list.append(df_top)

    # Combine the list of dfs into a df
    df_additional = pd.merge(*additional_df_list)

    # Add the org and append to df_combined_cumsum_additional
    df_additional["org"] = org
    df_combined_cumsum_additional = df_combined_cumsum_additional.append(df_additional)

# Now merge the additional df back onto to the main df so we now have the top
# license + language for each org at each day there was a change
df_combined_cumsum = pd.merge(df_combined_cumsum, df_combined_cumsum_additional)

# Output data

# Make the columns nice
df_combined_cumsum = df_combined_cumsum.rename(
    columns={
        "org": "Org",
        "link": "Link",
        "date": "Date",
        "open_repos": "Open Repos",
        "stargazers": "Stargazers",
        "forks": "Forks",
        "open_issues": "Open Issues",
        "license": "Top License",
        "language": "Top Language",
    }
)

# Format the output table (this is the latest row for each org)
df_combined_cumsum_latest = (
    df_combined_cumsum.sort_values("Date")
    .groupby("Org")
    .tail(1)
    .drop(columns="Date")
    .sort_values("Open Repos", ascending=False)
)

# Initialise plot
fig = make_subplots(
    rows=2,
    cols=1,
    vertical_spacing=0.1,
    specs=[[{"type": "scatter"}], [{"type": "table"}]],
)

# Loop over each org and add line to plot
for org in list(df_combined_cumsum_latest["Org"]):

    # Filter the df
    df_ = df_combined_cumsum[df_combined_cumsum["Org"] == org]

    # Add the trace plot
    fig.add_trace(
        go.Scatter(
            x=df_["Date"],
            y=df_["Open Repos"],
            mode="lines",
            name=org,
            line={"shape": "hvh"},
            # TODO: # Add discrete colour sequence if needed
        ),
        row=1,
        col=1,
    )

# Add the table
bold_header = [
    "<b>" + c + "<b>" for c in df_combined_cumsum_latest.columns if c != "Link"
]
hyperlinked_first_col = (
    "<a href='"
    + df_combined_cumsum_latest["Link"]
    + "'>"
    + df_combined_cumsum_latest["Org"]
    + "</a>"
).tolist()
remaining_cols = [
    df_combined_cumsum_latest[c].tolist() for c in df_combined_cumsum_latest.columns[2:]
]

fig.add_trace(
    go.Table(
        header=dict(
            values=bold_header,
            fill_color="white",  # If 'rgba(0, 0, 0, 0)' then information not hidden when scrolling
            align="left",
        ),
        cells=dict(
            values=[hyperlinked_first_col] + remaining_cols,
            fill_color="white",
            align="left",
        ),
    ),
    row=2,
    col=1,
)

# Asthetics of the plot
fig.update_layout(
    {"plot_bgcolor": "rgba(0, 0, 0, 0)", "paper_bgcolor": "rgba(0, 0, 0, 0)"},
    autosize=True,
    margin=dict(l=50, r=50, b=50, t=50, pad=4, autoexpand=True),
    height=1000,
    hovermode="x",
)

# Add title and dynamic range selector to x axis
fig.update_xaxes(
    title_text="Date",
    rangeselector=dict(
        buttons=list(
            [
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all"),
            ]
        )
    ),
)

# Add title to y axis
fig.update_yaxes(title_text="Open Repos")

# Write out to file (.html)
config = {"displayModeBar": False, "displaylogo": False}
plotly_obj = plotly.offline.plot(
    fig, include_plotlyjs=False, output_type="div", config=config
)
with open("_includes/plotly_obj.html", "w") as file:
    file.write(plotly_obj)

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