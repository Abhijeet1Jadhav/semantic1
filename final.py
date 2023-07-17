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
    run_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}'
    jobs_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}/jobs'

    # Make a GET request to fetch run details
    run_response = requests.get(run_url, headers=headers)
    if run_response.status_code == 200:
        run_details = run_response.json()
        run_name = run_details['name']
        run_number = run_details['run_number']
        run_attempt = run_details['run_attempt']
        head_commit_message = run_details['head_commit']['message']
        author = run_details['head_commit']['author']['name']
    else:
        print(f'Failed to retrieve run details for run ID: {run_id}')
        return None

    # Make a GET request to fetch job details
    jobs_response = requests.get(jobs_url, headers=headers)
    if jobs_response.status_code == 200:
        jobs = jobs_response.json()['jobs']
        job_steps = []

        for job in jobs:
            job_name = job['name']
            job_start_time = job['started_at']
            job_end_time = job['completed_at']
            job_status = job['status']
            job_conclusion = job['conclusion']

            # Get the pull request details if the workflow is triggered by a pull request
            if 'pull_request' in job:
                pull_request = job['pull_request']
                pr_number = pull_request['number']
                pr_title = pull_request['title']
            else:
                pr_number = None
                pr_title = None

            # Iterate over each step in the job
            for step in job['steps']:
                step_name = step['name']
                status = step['status']
                conclusion = step['conclusion'] if 'conclusion' in step else None
                step_number = step['number']
                started_at = step['started_at']
                completed_at = step['completed_at']

                job_steps.append({
                    'Run Name': run_name,
                    'Job Name': job_name,
                    'Step Name': step_name,
                    'Job Start Time': job_start_time,
                    'Job End Time': job_end_time,
                    'Job Status': job_status,
                    'Job Conclusion': job_conclusion,
                    'Pull Request Number': pr_number,
                    'Pull Request Title': pr_title,
                    'Status': status,
                    'Conclusion': conclusion,
                    'Step Number': step_number,
                    'Started At': started_at,
                    'Completed At': completed_at
                })

        return job_steps
    else:
        print(f'Failed to retrieve job steps for run ID: {run_id}')
        return None

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
    pivot_table = df.pivot_table(index=['Run Name', 'Job Name', 'Step Name'], columns='Job Conclusion', aggfunc=len, fill_value=0, margins=True, margins_name='Total')

    # Save the pivot table to a new CSV file
    pivot_csv_file = 'pivot_table.csv'
    pivot_table.to_csv(pivot_csv_file)
    print(f'Successfully created the pivot table and saved it as "{pivot_csv_file}".')

    # Upload the workflow data CSV file as an artifact
    upload_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/artifacts'
    workflow_artifact_name = 'workflow_steps_artifact'

    workflow_response = requests.post(
        upload_url,
        headers=headers,
        json={
            'artifact_name': workflow_steps_artifact,
            'size': os.path.getsize(csv_file),
            'file_paths': [csv_file]
        }
    )

    if workflow_response.status_code == 201:
        print(f'Workflow data CSV file "{csv_file}" uploaded as artifact with name "{workflow_artifact_name}"')
    else:
        print(f'Failed to upload workflow data CSV artifact. Status Code: {workflow_response.status_code}')
        print(workflow_response.text)

    # Upload the pivot table CSV file as an artifact
    pivot_artifact_name = 'pivot_table_artifact'

    pivot_response = requests.post(
        upload_url,
        headers=headers,
        json={
            'artifact_name': pivot_artifact_name,
            'size': os.path.getsize(pivot_csv_file),
            'file_paths': [pivot_csv_file]
        }
    )

    if pivot_response.status_code == 201:
        print(f'Pivot table CSV file "{pivot_csv_file}" uploaded as artifact with name "{pivot_artifact_name}"')
    else:
        print(f'Failed to upload pivot table CSV artifact. Status Code: {pivot_response.status_code}')
        print(pivot_response.text)

else:
    print(f'Failed to retrieve workflow runs. Status Code: {response.status_code}')
    print(response.text)
