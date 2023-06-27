import requests
import csv

workflow_run_id = "9781817810"
repo_owner = "Abhijeet1Jadhav"
repo_name = "semantic1"
access_token = "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"

# Get the workflow run details
url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/runs/{workflow_run_id}"
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(url, headers=headers)
response_json = response.json()
workflow_jobs = response_json["workflow_run_id"]["jobs"]

# Extract job steps outputs and store in CSV
output_rows = []
for job in workflow_jobs:
    job_name = job["name"]
    steps = job["steps"]
