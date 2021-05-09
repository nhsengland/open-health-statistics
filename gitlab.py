import pandas as pd
import urllib.request  # https://stackoverflow.com/a/41217363
import json
import time

def pull_raw_df(group_dict):
    
    # Initialise a dataframe
    df = pd.DataFrame()
    
    # Pull GitLab data from the API
    for group_name, group_id in group_dict.items():
        data = [1]
        page = 1
        while bool(data) is True:
            url = (
                "https://gitlab.com/api/v4/groups/"
                + group_id
                + "/projects?include_subgroups=true&page="
                + str(page)
                + "&per_page=100"
            )
            response = urllib.request.urlopen(url)
            data = json.loads(response.read())
            flat_data = pd.json_normalize(data)
            flat_data["org"] = group_name
            df = df.append(flat_data)
            page = page + 1
            time.sleep(0.2) # Avoid unauthenticated requests limit (10 per sec)
            
    # Additionally get the license + language data for each project
    
    # Get the project ids
    project_ids = list(df["id"].astype(int))
        
    # Initialise lists to store them in
    licenses = []
    top_languages = []
    
    # Pull additional GitLab data from the API 
    for project_id in project_ids:
    
        # Then get the license for each project
        url = (
            "https://gitlab.com/api/v4/projects/" 
            + str(project_id) 
            + "?license=true"
        )
        response = urllib.request.urlopen(url)
        license_dict = json.loads(response.read())["license"]
        license_ = license_dict.get("name") if license_dict else None
    
        # Then get the top language for each project
        url = (
            "https://gitlab.com/api/v4/projects/" 
            + str(project_id) 
            + "/languages"
        )
        response = urllib.request.urlopen(url)
        languages = json.loads(response.read())
        top_language = max(languages, key=languages.get) if languages else None
    
        # Append the data
        licenses.append(license_)
        top_languages.append(top_language)
    
    # Add the extra columns to the df
    df["license"] = licenses
    df["language"] = top_languages
            
    return df


def tidy_raw_df(df):
    
    # Add a column of 1s to sum for open_repos (this enables us to use sum() on 
    # all columns later)
    df["open_repos"] = 1
    
    # Add the link
    df["link"] = (
        "https://gitlab.com/" 
        + df["namespace.full_path"].apply(lambda x: x.split("/")[0])
    )

    # Filter and rename columns
    df = df[
        [
            "org",
            "link",
            "created_at",
            "open_repos",
            "star_count",
            "forks_count",
            "open_issues_count",
            "license",
            "language"
        ]
    ].rename(
        columns={
            "created_at": "date",
            "star_count": "stargazers",
            "forks_count": "forks",
            "open_issues_count": "open_issues"
        }
    )
        
    return df