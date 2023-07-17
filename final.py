import csv
import requests
import os
import pandas as pd

# Replace with your personal access token
ACCESS_TOKEN = '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'

# Replace with your repository details
REPO_OWNER = 'Abhijeet1Jadhav'
REPO_NAME = 'semantic1'
WORKFLOW_FILE = 'steps.yml'

# Set the headers including the access token
headers = {
    'Authorization': f'token {ACCESS_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

# Function to fetch run details and job steps for a given run ID
def fetch_run_and_job_steps(run_id):
    # ... (existing code for fetching run and job steps)

# Make a GET request to retrieve workflow runs
    api_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{WORKFLOW_FILE}/runs'
    response = requests.get(api_url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    runs = response.json()['workflow_runs']

    # Create a list to store all data
    all_data = []

    # Iterate over each run
    for run in runs:
        run_id = run['id']
        job_steps = fetch_run_and_job_steps(run_id)

        if job_steps:
            all_data.extend(job_steps)

    # Write all data to a CSV file
    csv_file = 'workflow_runs_data.csv'
    with open(csv_file, mode='w', newline='') as file:
        fieldnames = ['Run Name', 'Job Name', 'Step Name', 'Job Start Time', 'Job End Time', 'Job Status', 'Job Conclusion', 'Pull Request Number', 'Pull Request Title', 'Status', 'Conclusion', 'Step Number', 'Started At', 'Completed At']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_data)

    print(f'Successfully captured all workflow steps data in "{csv_file}".')

    # Create a DataFrame from the data
    df = pd.DataFrame(all_data, columns=fieldnames)

    # Create a pivot table with the desired settings
    pivot_table = df.pivot_table(index=['Run Name', 'Job Name'], columns=['Step Name', 'Job Conclusion'], aggfunc='size', fill_value=0, margins=True, margins_name='Total')

    # Save the pivot table to a new CSV file
    pivot_csv_file = 'pivot_table.csv'
    pivot_table.to_csv(pivot_csv_file)
    print(f'Successfully created the pivot table and saved it as "{pivot_csv_file}".')

    # Upload the CSV file as an artifact
    upload_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/artifacts'
    artifact_name = 'workflow_steps_artifact'

    # Upload the CSV file as an artifact
    csv_response = requests.post(
        upload_url,
        headers=headers,
        json={
            'artifact_name': artifact_name,
            'size': os.path.getsize(csv_file),
            'file_paths': [csv_file]
        }
    )

    if csv_response.status_code == 201:
        print(f'CSV file "{csv_file}" uploaded as artifact with name "{artifact_name}"')
    else:
        print(f'Failed to upload CSV artifact. Status Code: {csv_response.status_code}')
        print(csv_response.text)

    # Upload the pivot table as an artifact
    pivot_response = requests.post(
        upload_url,
        headers=headers,
        json={
            'artifact_name': workflow_steps_artifact,
            'size': os.path.getsize(pivot_csv_file),
            'file_paths': [pivot_csv_file]
        }
    )

    if pivot_response.status_code == 201:
        print(f'Pivot table "{pivot_csv_file}" uploaded as artifact with name "{artifact_name}"')
    else:
        print(f'Failed to upload pivot table artifact. Status Code: {pivot_response.status_code}')
        print(pivot_response.text)

else:
    print(f'Failed to retrieve workflow runs. Status Code: {response.status_code}')
    print(response.text)
