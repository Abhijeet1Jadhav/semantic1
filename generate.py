import os
from github import Github
import pandas as pd

# Access GitHub repository using authentication token
token = os.getenv('RELEASE_GIT_TOKEN')
g = Github(token)
repo = g.get_repo('Abhijeet1Jadhav/semantic1')  # Replace with your repository details

# Fetch pull requests
pull_requests = repo.get_pulls(state='open')

# Prepare data for CSV
data = []
for pr in pull_requests:
    data.append({
        'Number': pr.number,
        'Title': pr.title,
        'Author': pr.user.login,
        'URL': pr.html_url
    })

# Create DataFrame and save as CSV
df = pd.DataFrame(data)
df.to_csv('pull_requests.csv', index=False)
