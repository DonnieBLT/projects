import json
import re
import requests
from bs4 import BeautifulSoup

def extract_github_links(url):
    print("url", url)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=True)
    github_links = [link['href'] for link in links if 'github.com' in link['href']]
    print("github_links", github_links)
    return github_links

with open('www_project_repos.json', 'r') as f:
    data = json.load(f)

project_links = []

for project in data:
    print("project name", project['name'])
    project_name = project['name']
    repo_links = extract_github_links(project['html_url'])
    project_links.append({
        'project_name': project_name,
        'repo_links': repo_links
    })

with open('project_repos_links.json', 'w') as f:
    json.dump(project_links, f, indent=2)
