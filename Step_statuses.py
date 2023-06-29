import csv
import requests
import os

# Replace with your personal access token
ACCESS_TOKEN = '${{ secrets.RELEASE_GIT_TOKEN }}'

# Replace with your repository details
REPO_OWNER = 'Abhijeet1Jadhav'
REPO_NAME = 'semantic1'
WORKFLOW_FILE = 'extraction.yml'

# Define the API endpoint
api_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{WORKFLOW_FILE}/runs'

# Set the headers including the access token
headers = {
    'Authorization': f'token {ACCESS_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

# Make a GET request to retrieve the workflow runs
response = requests.get(api_url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    runs = response.json()['workflow_runs']

    # Create a list to hold the status of steps
    steps_status = []

    # Counter for dev environment deployments
    dev_deployments = 0

    # Iterate over each run
    for run in runs:
        run_id = run['id']
        run_jobs_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}/jobs'

        # Make a GET request to fetch the jobs of the run
        response = requests.get(run_jobs_url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            jobs = response.json()['jobs']

            # Iterate over each job in the run
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
                    status = step['conclusion'] if step['conclusion'] else 'in_progress'

                    steps_status.append({
                        'Run ID': run_id,
                        'Job Name': job_name,
                        'Step Name': step_name,
                        'Status': status,
                        'Pull Request Number': pr_number,
                        'Pull Request Title': pr_title
                    })

                    # Count the number of deployments on dev environment
                    if job_name == 'Deployment to Dev':
                        dev_deployments += 1

    # Define the CSV file path
    csv_file = 'workflow_steps_status.csv'

    # Write the steps status to a CSV file
    with open(csv_file, mode='w', newline='') as file:
        fieldnames = ['Run ID', 'Job Name', 'Step Name', 'Status', 'Pull Request Number', 'Pull Request Title']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(steps_status)

    print(f'Successfully captured the steps status in "{csv_file}".')

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
