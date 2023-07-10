import csv
import requests
import os

# Replace with your personal access token
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']

# Replace with your repository details
REPO_OWNER = 'Abhijeet1Jadhav'
REPO_NAME = 'semantic1'
#WORKFLOW_FILE = 'steps.yml'
WORKFLOW_FILE = sys.argv[1]

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
                    'Job Name': job_name,
                    'Pull Request Number': pr_number,
                    'Pull Request Title': pr_title,
                    'Step Name': step_name,
                    'Status': status,
                    'Conclusion': conclusion,
                    'Step Number': step_number,
                    'Started At': started_at,
                    'Completed At': completed_at
                })

        return {
            'Run ID': run_id,
            'Run Name': run_name,
            'Run Number': run_number,
            'Run Attempt': run_attempt,
            'Head Commit Message': head_commit_message,
            'Author': author,
            'Job Steps': job_steps
        }
    else:
        print(f'Failed to retrieve job steps for run ID: {run_id}')
        return None

# Make a GET request to retrieve workflow runs
api_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{WORKFLOW_FILE}/runs'
response = requests.get(api_url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    runs = response.json()['workflow_runs']

    # Variables to store deployment count
    dev_deployments = 0
    prod_deployments = 0
    test_deployments = 0

    # Iterate over each run
    runs_data = []
    for run in runs:
        run_id = run['id']
        run_and_job_steps = fetch_run_and_job_steps(run_id)

        if run_and_job_steps:
            runs_data.append(run_and_job_steps)

            # Count the number of deployments to each environment
            for job_step in run_and_job_steps['Job Steps']:
                job_name = job_step['Job Name']
                if job_name == 'Deployment to Dev':
                    dev_deployments += 1
                elif job_name == 'Deployment to Prod':
                    prod_deployments += 1
                elif job_name == 'Deployment to Test':
                    test_deployments += 1

    # Write the runs data to a CSV file
    csv_file = 'workflow_runs_data.csv'
    with open(csv_file, mode='w', newline='') as file:
        fieldnames = ['Run ID', 'Run Name', 'Run Number', 'Run Attempt', 'Head Commit Message', 'Author', 'Job Name', 'Pull Request Number', 'Pull Request Title', 'Step Name', 'Status', 'Conclusion', 'Step Number', 'Started At', 'Completed At']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for run_data in runs_data:
            run_id = run_data['Run ID']
            run_name = run_data['Run Name']
            run_number = run_data['Run Number']
            run_attempt = run_data['Run Attempt']
            head_commit_message = run_data['Head Commit Message']
            author = run_data['Author']

            # Iterate over each job step in the run
            for job_step in run_data['Job Steps']:
                job_name = job_step['Job Name']
                pr_number = job_step['Pull Request Number']
                pr_title = job_step['Pull Request Title']
                step_name = job_step['Step Name']
                status = job_step['Status']
                conclusion = job_step['Conclusion']
                step_number = job_step['Step Number']
                started_at = job_step['Started At']
                completed_at = job_step['Completed At']

                # Write the data to the CSV file
                writer.writerow({
                    'Run ID': run_id,
                    'Run Name': run_name,
                    'Run Number': run_number,
                    'Run Attempt': run_attempt,
                    'Head Commit Message': head_commit_message,
                    'Author': author,
                    'Job Name': job_name,
                    'Pull Request Number': pr_number,
                    'Pull Request Title': pr_title,
                    'Step Name': step_name,
                    'Status': status,
                    'Conclusion': conclusion,
                    'Step Number': step_number,
                    'Started At': started_at,
                    'Completed At': completed_at
                })

    print(f'Successfully captured the workflow runs data in "{csv_file}".')

    # Write the deployment count to the same CSV file
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([])
        writer.writerow(['Deployment Count'])
        writer.writerow(['Environment', 'Count'])
        writer.writerow(['Dev', dev_deployments])
        writer.writerow(['Prod', prod_deployments])
        writer.writerow(['Test', test_deployments])

    # Upload the CSV file as an artifact
    upload_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/artifacts'
    artifact_name = 'workflow_steps_artifact'

    response = requests.post(
        upload_url,
        headers=headers,
        json={
            'artifact_name': artifact_name,
            'size': os.path.getsize(csv_file),
            'file_paths': [csv_file]
        }
    )

    if response.status_code == 201:
        print(f'CSV file "{csv_file}" uploaded as artifact with name "{artifact_name}"')
    else:
        print(f'Failed to upload artifact. Status Code: {response.status_code}')
        print(response.text)
else:
    print(f'Failed to retrieve workflow runs. Status Code: {response.status_code}')
    print(response.text)
