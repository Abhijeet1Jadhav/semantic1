import requests
import csv
import os

repository_owner = 'Abhijeet1Jadhav'
repository_name = 'semantic1'
workflow_name = 'Deployment'
auth_token = os.environ['RELEASE_GIT_TOKEN']

def fetch_workflow_runs():
    url = f"https://api.github.com/repos/{repository_owner}/{repository_name}/actions/workflows/{workflow_name}/runs"
    headers = {
        'Authorization': f'token {auth_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def write_workflow_runs_to_csv(workflow_runs):
    with open('workflow_runs.csv', 'w', newline='') as csvfile:
        fieldnames = ['Run ID', 'Status', 'Conclusion']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for run in workflow_runs['workflow_runs']:
            writer.writerow({
                'Run ID': run['id'],
                'Status': run['status'],
                'Conclusion': run['conclusion']
            })

workflow_runs = fetch_workflow_runs()
write_workflow_runs_to_csv(workflow_runs)
