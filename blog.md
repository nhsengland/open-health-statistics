# Open Health Statistics - How it's made

## End-to-end open analytics

1. [GitHub](https://docs.github.com/en/rest/reference/orgs) / [GitLab API](): use python to pull data from the APIs and do the calcs
2. [Plotly](https://plotly.com/graphing-libraries/): Open source graphing library used to plot the data and tables to interactive charts
3. [GitHub Actions](https://github.com/features/actions): orchestrate and automate the first two components on a daily basis, commits back to the repo
4. [GitHub.io Pages](https://pages.github.com/): publishe and host the results to a static website that re-builds on a new commit

## [Github](https://docs.github.com/en/rest/reference/orgs) / [GitLab API]()

## [Github Actions](https://github.com/features/actions)

GitHub Actions makes it easy to automate all your software workflows. So you can build, test, and deploy your code right from GitHub. It's free on public repositories.

Workflow files use [YAML syntax](https://learnxinyminutes.com/docs/yaml/).

You must store workflow files in the `.github/workflows` directory of your repository.

### Requred

```bash
name
```

The name of your workflow. GitHub displays the names of your workflows on your repository's actions page.

```bash
on
```

Required. The name of the GitHub event that triggers the workflow. For a list of available events, see [Events that trigger workflows](https://docs.github.com/en/actions/reference/events-that-trigger-workflows).

### Example using a single event

```bash
on: push
```

Triggered when code is pushed to any branch in a repository

### Example using a list of events

```bash
on: [push, pull_request]
```

### Triggers the workflow on push or pull request events

```bash
on.schedule
```

You can schedule a workflow to run at specific UTC times using POSIX cron syntax. Scheduled workflows run on the latest commit on the default or base branch.

This example triggers the workflow every day at 5:30 and 17:30 UTC:

```bash
on:
  schedule:
    #runs at 00:00 UTC everyday
    - cron: "0 0 * * *"
```

### Jobs

A workflow run is made up of one or more jobs. Each job runs in a fresh instance of a virtual environment specified by `runs-on`.

| Virtual environment  | YAML workflow label                |
| -------------------- | ---------------------------------- |
| Windows Server 2019  | `windows-latest` or `windows-2019` |
| Windows Server 2016  | `windows-2016`                     |
| Ubuntu 20.04         | `ubuntu-latest` or `ubuntu-20.04`  |
| Ubuntu 18.04         | `ubuntu-18.04`                     |
| macOS Big Sur 11     | `macos-11`                         |
| macOS Catalina 10.15 | `macos-latest` or `macos-10.15`    |

### Steps

[Checkout](https://github.com/actions/checkout): This action checks-out your repository so the workflow can access it.

```bash
- name: checkout repo content
uses: actions/checkout@v2
```

[Setup python](https://github.com/actions/setup-python): This action sets up a Python environment for use in actions by installing and adding to PATH an available version of Python in this case python 3.8

```bash
- name: setup python
uses: actions/setup-python@v2
with:
    python-version: 3.8
```

[Install dependancies](https://github.com/py-actions/py-dependency-install): This GitHub Action installs Python package dependencies from a user-defined `requirements.txt` file path with `pip`

```bash
- name: Install Python dependencies
uses: py-actions/py-dependency-install@v2
with:
    path: "requirements.txt"
```

In this case plotly, pandas, and pyYaml

```bash
# requirements.txt
plotly==4.14.3
pandas==1.1.3
pyyaml==5.4.1
```

Runs command-line programs using the operating system's shell. run the run.py to get the latest data

```bash
- name: execute py script
run: |
    python run.py
        dir
```

Commit changes to files

```bash
- name: Commit files
id: commit
run: |
    git config --local user.email "action@github.com"
    git config --local user.name "github-actions"
    git add --all
    if [-z "$(git status --porcelain)"]; then
        echo "::set-output name=push::false"
    else
        git commit -m "Add changes" -a
        echo "::set-output name=push::true"
    fi
shell: bash
```

Push changes to repo so github pages will re-build website

```bash
- name: Push changes
if: steps.commit.outputs.push == 'true'
uses: ad-m/github-push-action@master
with:
    github_token: ${{ secrets.GITHUB_TOKEN }}}
```

## GitHub Pages

GitHub Pages is a static site hosting service that takes HTML, CSS, and JavaScript files straight from a repository on GitHub, optionally runs the files through a build process, and publishes a website.

GitHub Pages publishes any static files that you push to your repository. You can create your own static files or use a static site generator to build your site for you

We are using a static version of the NHSD Digital Service Manual

### Usage limits

GitHub Pages sites are subject to the following usage limits:

- GitHub Pages source repositories have a recommended limit of 1GB.
- Published GitHub Pages sites may be no larger than 1 GB.
- GitHub Pages sites have a _soft_ bandwidth limit of 100GB per month.
- GitHub Pages sites have a _soft_ limit of 10 builds per hour.
