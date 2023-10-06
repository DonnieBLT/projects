import os
import json
import requests
from datetime import datetime, timedelta

GITHUB_API_URL = "https://api.github.com"
ORG_NAME = "owasp"
REPO_PREFIX = "www-project"
OUTPUT_FILE = "www_project_repos.json"
SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL_SWEEP"]
SEARCH_STRING = "This is an example of a Project or Chapter Page"

headers = {"Authorization": f"token {os.environ['GITHUB_TOKEN']}"}

def get_repos():
    all_repos = []
    page = 1
    max_pages = 20

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
    
def get_index_md_content(repo_full_name):
    url = f"{GITHUB_API_URL}/repos/{repo_full_name}/contents/index.md"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_content = response.json()["content"]
        return file_content.decode('base64')
    return None

def check_last_updated_date(repo_full_name):
    url = f"{GITHUB_API_URL}/repos/{repo_full_name}/commits?path=index.md&per_page=1"
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json():
        last_updated_date = response.json()[0]['commit']['committer']['date']
        return datetime.strptime(last_updated_date, "%Y-%m-%dT%H:%M:%SZ")
    return None

def send_slack_alert(message):
    payload = {"text": message}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    response.raise_for_status()

def main():
    print('Parsing repos...')
    repos = get_repos()
    www_project_repos = filter_and_format_repos(repos)
    
    for repo in www_project_repos:
        repo_full_name = repo['full_name']
        index_md_content = get_index_md_content(repo_full_name)
        
        if index_md_content and SEARCH_STRING not in index_md_content:
            last_updated_date = check_last_updated_date(repo_full_name)
            if last_updated_date and datetime.utcnow() - last_updated_date > timedelta(days=30):
                send_slack_alert(f"Repo {repo_full_name} has not been updated in over a month. Check index.md.")
            
if __name__ == "__main__":
    main()
