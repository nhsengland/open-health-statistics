import os
import urllib
import json
import pandas as pd
from pandas import json_normalize
from datetime import datetime
from datetime import date
import time

orgs = ["nhsx", "111Online", "NHSDigital", "nhsconnect", "nhsengland"]

# GitHub API unauthenticated requests rate limit = 10 requests per minute.

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