import pandas as pd
import urllib.request  # https://stackoverflow.com/a/41217363
import json

def pull_raw_df(org_dict):
    
    # Initialise a dataframe
    df = pd.DataFrame()
    
    # Pull GitHub data from the API (note we can only make 60 calls per hour so
    # if we have over 60 orgs would have to try a different strategy)
    for org_name, org_id in org_dict.items():
        data = [1]
        page = 1
        while bool(data) is True:
            url = (
                "https://api.github.com/orgs/"
                + org_id
                + "/repos?page="
                + str(page)
                + "&per_page=100"
            )
            response = urllib.request.urlopen(url)
            data = json.loads(response.read())
            flat_data = pd.json_normalize(data)
            flat_data["org"] = org_name
            df = df.append(flat_data)
            page = page + 1
            
    return df


def tidy_raw_df(df):
    
    # Add a column of 1s to sum for open_repos (this enables us to use sum() on 
    # all columns later)
    df["open_repos"] = 1

    # Filter and rename columns
    df = df[
        [
            "org",
            "owner.html_url",
            "created_at",
            "open_repos",
            "stargazers_count",
            "forks_count",
            "open_issues_count",
            "license.name",
            "language"
        ]
    ].rename(
        columns={
            "owner.html_url": "link",
            "created_at": "date",
            "stargazers_count": "stargazers",
            "forks_count": "forks",
            "open_issues_count": "open_issues",
            "license.name": "license"
        }
    )
        
    return df