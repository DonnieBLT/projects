import os
import json
import requests

GITHUB_API_URL = "https://api.github.com"
ORG_NAME = "owasp"
REPO_PREFIX = "www-project"
OUTPUT_FILE = "www_project_repos.json"
SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]

def get_repos():
    all_repos = []
    page = 1
    max_pages = 20  # Set to 20 to fetch 2000 repositories (100 per page * 20 pages)

    headers = {"Authorization": f"token {os.environ['GITHUB_TOKEN']}"}

    while page <= max_pages:
        url = f"{GITHUB_API_URL}/orgs/{ORG_NAME}/repos?per_page=100&page={page}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        repos = response.json()
        if not repos:
            break

        all_repos.extend(repos)
        page += 1

    return all_repos

def filter_and_format_repos(repos):
    filtered_repos = []

    for repo in repos:
        print(repo)
        if repo["name"].startswith(REPO_PREFIX):
            filtered_repos.append(repo)

    return filtered_repos

def send_slack_alert(new_repos):
    message = "New repositories detected:\n"
    for repo in new_repos:
        message += f"- {repo['full_name']} ({repo['html_url']})\n"

    payload = {"text": message}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    response.raise_for_status()

def main():
    print('parsing repos')
    repos = get_repos()
    www_project_repos = filter_and_format_repos(repos)

    try:
        with open(OUTPUT_FILE, "r") as f:
            old_repos = json.load(f)
    except FileNotFoundError:
        old_repos = []

    new_repos = [repo for repo in www_project_repos if repo not in old_repos]
    if new_repos:
        send_slack_alert(new_repos)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(www_project_repos, f, indent=2)

if __name__ == "__main__":
    main()