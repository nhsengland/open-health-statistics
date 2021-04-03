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

orgs = ["nhsx", "111Online", "NHSDigital", "nhsconnect", "nhsengland"]

# GitHub API unauthenticated requests rate limit = 10 requests per minute.

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

df_group = df.groupby(["owner_login"]).agg(
    {
        # find the number of open repos
        "name": "count",
        "size": "sum",
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
    "Total Size",
    "Stargazers",
    "Forks",
    "Open Issues",
    "Top License",
    "Top Language",
]

df_html = df_group.head(10).to_html(classes="summary")
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

fig = px.bar(
    df,
    x=res["Date"],
    y=res["Repos Created"],
    labels={"y": "Repos Created", "x": "Date"},
    color=res["Org"],
    barmode="stack",
    color_discrete_sequence=px.colors.qualitative.T10,
    width=800,
    height=400,
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
    legend=dict(orientation="v", yanchor="top", y=0.99, xanchor="left", x=0.01),
)

plot_div = plotly.offline.plot(fig, include_plotlyjs=False, output_type="div")
# Write HTML String to file.html
with open("_includes/chart.html", "w") as file:
    file.write(plot_div)