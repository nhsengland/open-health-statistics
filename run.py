import yaml
import pandas as pd
from datetime import datetime
import plotly
import plotly.graph_objects as go
import plotly.express as px

import github as github
import gitlab as gitlab

# Load in the config parameters
with open("config.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

# Data collection

# Pull the raw data from the APIs
raw_github_df = github.pull_raw_df(config["github_org_dict"])
raw_gitlab_df = gitlab.pull_raw_df(config["gitlab_group_dict"])

# Tidy the raw data
tidy_github_df = github.tidy_raw_df(raw_github_df)
tidy_gitlab_df = gitlab.tidy_raw_df(raw_gitlab_df)

# Create a separate dataframe for the topics page and drop columns which 
# don't work with gitlab
df_topics = tidy_github_df
df = tidy_github_df.drop(columns='topics')
df = tidy_github_df.drop(columns='full_name')

# Combine tidy dataframes
df = pd.concat([tidy_github_df, tidy_gitlab_df]).reset_index(drop=True)

# -------------------------
# Data processing
# -------------------------

# Make an org_short hyperlink column and make the org column a hyperlink
df["org_short"] = (
    "<a href='"
    + df["link"]
    + "'>"
    + df["org"].apply(lambda x: x[:13] + "..." if len(x) > 16 else x)
    + "</a>"
)
df["org"] = "<a href='" + df["link"] + "'>" + df["org"] + "</a>"

# Now we have a standardised table we can begin to split and aggregate... start
# by changing date to a date type (day only)
df["date"] = pd.to_datetime(df["date"]).apply(lambda x: x.strftime("%Y-%m-%d"))

# Cumulative sum by org, link and date of the numerical columns
aggregate_df = (
    df.groupby(["org", "org_short", "date"])
    .sum()
    .groupby(level=[0])
    .cumsum()
    .reset_index()
)

# Now we need to get the top license + language at each date for each
# organisation. This is not so straight forward but wrapped in a function as
# is the same for both columns
def create_top_column_df(df, column):
    return (
        df
        # Get the count of new columns values at each date
        .groupby(["org", "date", column])
        .size()
        # Convert to a cumulative count of the column values
        .groupby(level=[0, 2])
        .cumsum()
        .reset_index(level=column)
        # Get a column per value
        .pivot(columns=column)
        .droplevel(0, axis=1)
        # Forward fill so that each column has the previous value until it
        # increases again
        .groupby(["org"])
        .ffill()
        # Convert to long and remove NaNs
        .reset_index()
        .melt(id_vars=["org", "date"], var_name=column, value_name="count")
        .dropna()
        # Keep the column value with the largest count each day
        .sort_values(by=["org", "date", "count"])
        .drop_duplicates(subset=["org", "date"], keep="last")
        # Get rid of the count column
        .drop(columns=["count"])
    )


top_license_df = create_top_column_df(df, "license")
top_language_df = create_top_column_df(df, "language")

# Now merge these back onto the aggregate_df
aggregate_df = (
    aggregate_df
    # Left join as we will not have a top license + language on a given date if
    # the column was a NaN or None
    .merge(top_license_df, how="left")
    .merge(top_language_df, how="left")
    # Forward fill so that NaN is the previous value - standdard .ffill()
    # doesn't work so has to be wrapped in a lambda
    # https://stackoverflow.com/questions/63272417/pandas-groupby-drops-group-columns-after-fillna-in-1-1-0
    .groupby(["org"])
    .apply(lambda df: df.ffill())
)

# Output data

# Make the columns nice
aggregate_df = aggregate_df.rename(
    columns={
        "org": "Organisation",
        "org_short": "Org Short",
        "date": "Date",
        "open_repos": "Open Repositories",
        "stargazers": "Stargazers",
        "forks": "Forks",
        "open_issues": "Open Issues",
        "license": "Top License",
        "language": "Top Language",
    }
)

# save file to .csv
aggregate_df.to_csv("assets/data/openhealthstats.csv", index=False)

# Format the latest output table
aggregate_latest_df = (
    aggregate_df.groupby("Organisation")
    .tail(1)
    .sort_values("Open Repositories", ascending=False)
    .drop(columns=["Org Short", "Date"])
)

# Create output table (NHS.UK version)
aggregate_latest_df[
    ["Open Repositories", "Stargazers", "Forks", "Open Issues"]
] = aggregate_latest_df[
    ["Open Repositories", "Stargazers", "Forks", "Open Issues"]
].astype(
    int
)
aggregate_latest_html = aggregate_latest_df.to_html(
    index=False, render_links=True, escape=False
)
aggregate_latest_html = aggregate_latest_html.replace(
    "dataframe", "nhsuk-table__panel-with-heading-tab"
)
aggregate_latest_html = aggregate_latest_html.replace('border="1"', "")
with open("_includes/NHSUK_table.html", "w") as file:
    file.write(aggregate_latest_html)

# Add todays date to a version of the latest output table
aggregate_latest_df_ = aggregate_latest_df.copy()
aggregate_latest_df_["Date"] = datetime.now().strftime("%Y-%m-%d")

# Add the latest output table as a final row on aggregate_df with todays date
aggregate_df = pd.concat([aggregate_df, aggregate_latest_df_])

# Use the ordering of the output table to ensure lines get added to the plot
# in the correct order
aggregate_df["Organisation"] = pd.Categorical(
    values=aggregate_df["Organisation"],
    categories=aggregate_latest_df["Organisation"],
    ordered=True,
)

# Initialise plot
fig = go.Figure()

# Loop over each org and add line to plot
for (_, org_short), org_df in aggregate_df.groupby(["Organisation", "Org Short"]):

    # Add the trace plot
    fig.add_trace(
        go.Scatter(
            x=org_df["Date"],
            y=org_df["Open Repositories"],
            mode="lines",
            name=org_short,
            line={"shape": "hvh"},
        )
    )

# Make our own colour scale from plotly.express
colour_scale = px.colors.qualitative.Dark24 + px.colors.qualitative.Light24

# Loop through chart after adding traces to change colours
num_orgs = len(aggregate_df["Organisation"].unique())
for i in list(range(num_orgs)):
    fig["data"][i]["line"]["color"] = colour_scale[i]

# Asthetics of the plot
fig.update_layout(
    {
        "plot_bgcolor": "rgba(240, 244, 245, 1)",
        "paper_bgcolor": "rgba(240, 244, 245, 1)",
    },
    autosize=True,
    margin=dict(l=50, r=50, b=50, t=50, pad=4, autoexpand=True),
    height=500,
    hovermode="x",
)

# Add title and dynamic range selector to x axis
fig.update_xaxes(
    title_text="<b>" + "Date" + "<b>",
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
fig.update_yaxes(title_text="<b>" + "Open Repositories" + "<b>")

# Write out to file (.html)
config = {"displayModeBar": False, "displaylogo": False}
plotly_chart = plotly.offline.plot(
    fig, include_plotlyjs=False, output_type="div", config=config
)
with open("_includes/plotly_chart.html", "w") as file:
    file.write(plotly_chart)

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


# ----------------------------------------------
# August 2023 - add topics page
# ----------------------------------------------

# We need to change date to a date type (day only) again (TODO - CONSOLIDATE)
df_topics["date"] = pd.to_datetime(df_topics["date"],format='ISO8601').apply(lambda x: x.strftime("%Y-%m-%d"))

# Separate topics into different columns 
df_topics = df_topics['topics'].str.join('|').str.get_dummies()

# Separate topics into different columns 
df_topics['full_name'] = df['full_name']
df_topics['date'] = df["date"]

# Filter to columns in tag list (see config.yaml)
df_topics_filter = df_topics[df_topics.columns.intersection(github_tag_lst)]

# Filter to rows with non-zero values
df_topics_filter = df_topics_filter.loc[~(df_topics_filter.drop(["full_name","date"],axis=1)==0).all(axis=1)]

# Order by Tags, Date, Org
df_topics_filter = df_topics_filter.sort_values(github_tag_lst) 

# new data frame with split value columns
new = df_topics_filter["full_name"].str.split(pat="/", n=-1, expand=True)
 
# making separate first name column from new data frame
df_topics_filter["Org"]= new[0]
 
# making separate last name column from new data frame
df_topics_filter["Repo"]= new[1]
 
# Dropping old Name columns
df_topics_filter.drop(columns =["full_name"], inplace = True)

# Make an org_short hyperlink column and make the org column a hyperlink
df_topics_filter["Repo"] = "<a href='https://github.com/" + df_topics_filter["Org"] + "/" + df_topics_filter["Repo"] + "'>" + df_topics_filter["Repo"] + "</a>"

# Rotate the column names by 90 degrees
df_topics_filter = df_topics_filter.style.set_table_styles(
    [dict(selector="th",props=[('max-width', '100px')]),
        dict(selector="th.col_heading",
                 props=[("vertical-align", "text-top"), 
                        ('transform', 'rotateZ(-90deg)'),
                        ])]
)

# Save data frame as html table
df_topics_filter_html = df_topics_filter.to_html(
    index=False, render_links=True, escape=False
)
df_topics_filter_html = df_topics_filter_html.replace(
    "dataframe", "nhsuk-table__panel-with-heading-tab"
)
df_topics_filter_html = df_topics_filter_html.replace('border="1"', "")

with open("_includes/topics.html", "w") as file:
    file.write(df_topics_filter_html)
    
