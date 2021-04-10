import os
import urllib
import urllib.request
import json
import pandas as pd
from pandas import json_normalize
from datetime import datetime
from datetime import date
import time
import plotly
import plotly.express as px

orgs = [
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

## GitHub API unauthenticated requests rate limit = 10 requests per minute.

df = pd.DataFrame()
for org in orgs:
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
        df = df.append(flat_data)
        page = page + 1
        time.sleep(10)  # Sleep to avoid rate limit
df.columns = df.columns.str.replace(".", "_")

## Gitlab

url = (
    "https://gitlab.com/api/v4/groups/2955125/projects?include_subgroups=true"  # NHSBSA
)

df_gitlab = pd.DataFrame()
response = urllib.request.urlopen(url)
data = json.loads(response.read())
flat_data = json_normalize(data)
df_gitlab = df_gitlab.append(flat_data)
df_gitlab[
    ["owner_login", "group_path", "subgroup_path", "subsubgroup_path"]
] = df_gitlab["path_with_namespace"].str.split("/", expand=True)

df_gitlab_group = df_gitlab.groupby(["owner_login"]).agg(
    {
        # find the number of open repos
        "name": "count",
        "star_count": "sum",
        "forks_count": "sum",
        "open_issues_count": "sum",
        # "license_name": lambda x: x.value_counts().index[0],
        # "language": lambda x: x.value_counts().index[0],
    }
)
df_gitlab_group = df_gitlab_group.reset_index()
df_gitlab_group["license_name"] = "null"
df_gitlab_group["language"] = "null"
df_gitlab_group = df_gitlab_group[
    [
        "owner_login",
        "name",
        "star_count",
        "forks_count",
        "open_issues_count",
        "license_name",
        "language",
    ]
]
df_gitlab_group.columns = [
    "Org",
    "Open Repos",
    "Stargazers",
    "Forks",
    "Open Issues",
    "Top License",
    "Top Language",
]

df_gitlab["created_at"] = pd.to_datetime(df_gitlab["created_at"])
df_gitlab.set_index("created_at")
res_gitlab = df_gitlab.groupby(
    [pd.Grouper(key="created_at", freq="M"), "owner_login"]
).agg(
    {
        # find the number of open repos
        "name": "count",
    }
)  # .groupby('owner_login').cumsum()
res_gitlab = res_gitlab.reset_index()
res_gitlab.columns = ["Date", "Org", "Repos Created"]

df_group = df.groupby(["owner_login"]).agg(
    {
        # find the number of open repos
        "name": "count",
        "stargazers_count": "sum",
        "forks_count": "sum",
        "open_issues_count": "sum",
        "license_name": lambda x: x.value_counts().index[0],
        "language": lambda x: x.value_counts().index[0],
    }
)
df_group = df_group.reset_index()
df_group.columns = [
    "Org",
    "Open Repos",
    "Stargazers",
    "Forks",
    "Open Issues",
    "Top License",
    "Top Language",
]

df_all = pd.concat([df_group, df_gitlab_group], ignore_index=True, sort=False)
df_html = df_all.to_html(classes="summary")
# Write HTML String to file.html
with open("_includes/table.html", "w") as file:
    file.write(df_html)

data_updated = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
html_str = (
    '<p><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16"><path fill-rule="evenodd" d="M1.5 8a6.5 6.5 0 1113 0 6.5 6.5 0 01-13 0zM8 0a8 8 0 100 16A8 8 0 008 0zm.5 4.75a.75.75 0 00-1.5 0v3.5a.75.75 0 00.471.696l2.5 1a.75.75 0 00.557-1.392L8.5 7.742V4.75z"></path></svg> Latest Data: '
    + data_updated
    + "</p>"
)
with open("_includes/update.html", "w") as file:
    file.write(html_str)

df["created_at"] = pd.to_datetime(df["created_at"])
df.set_index("created_at")
res = df.groupby([pd.Grouper(key="created_at", freq="M"), "owner_login"]).agg(
    {
        # find the number of open repos
        "name": "count",
    }
)  # .groupby('owner_login').cumsum()
res = res.reset_index()
res.columns = ["Date", "Org", "Repos Created"]
res_all = pd.concat([res, res_gitlab], ignore_index=True, sort=False)

fig = px.bar(
    res_all,
    x="Date",
    y="Repos Created",
    # labels={"y": "Repos Created", "x": "Date"},
    color="Org",
    barmode="stack",
    color_discrete_sequence=px.colors.qualitative.T10,
)

fig.update_xaxes(
    # rangeslider_visible=True,
    rangeselector=dict(
        buttons=list(
            [
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all"),
            ]
        )
    )
)

fig.update_layout(
    {
        "plot_bgcolor": "rgba(0, 0, 0, 0)",
        "paper_bgcolor": "rgba(0, 0, 0, 0)",
    },
    legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="left", x=0),
    autosize=False,
    width=500,
    height=400,
)

plot_div = plotly.offline.plot(fig, include_plotlyjs=False, output_type="div")
# Write HTML String to file.html
with open("_includes/chart.html", "w") as file:
    file.write(plot_div)