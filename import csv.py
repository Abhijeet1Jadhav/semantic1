import os
import csv
import requests
import pandas as pd
from github import Github
import sys
from jira import JIRA
import base64
import time

# Replace with your GitHub repository details
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']

# Replace with your repository details
REPO_OWNER = 'Abhijeet1Jadhav'
REPO_NAME = 'demorelease'
WORKFLOWS_FOLDER = 'workflow_files'

headers = {
    'Authorization': f'token {ACCESS_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def fetch_run_and_job_steps(workflow_name, workflow_runs):
    run_and_job_steps = []

    for workflow_run in workflow_runs:
        run_id = workflow_run.id

        # Make a GET request to retrieve job details for the workflow run
        api_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}/jobs'
        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            jobs = response.json()['jobs']

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

                    run_and_job_steps.append({
                        'Run ID': run_id,
                        'Run Name': workflow_name,
                        'Repository Name': f'{REPO_OWNER}/{REPO_NAME}',
                        'Run Number': workflow_run.run_number,
                        'Run Attempt': workflow_run.run_attempt,
                        'Head Commit Message': workflow_run.head_commit.message,
                        'Author': workflow_run.head_commit.author.name,
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

        else:
            print(f'Failed to retrieve job details for workflow run ID: {run_id}')

    return run_and_job_steps

# Connect to GitHub using the access token
g = Github(ACCESS_TOKEN)

# Fetch and store the enabled workflow names in a variable
repo = g.get_repo(f'{REPO_OWNER}/{REPO_NAME}')
workflows_folder = repo.get_contents('.github/workflows')
workflow_names_list = [file.name for file in workflows_folder if file.type == 'file']

# Create a dictionary to store data for each workflow file
workflow_data_dict = {}

# Iterate over each workflow name and process its data
for workflow_name in workflow_names_list:
    workflow = repo.get_workflow(workflow_name)
    workflow_runs = workflow.get_runs()
    workflow_data = fetch_run_and_job_steps(workflow_name, workflow_runs)
    workflow_data_dict[workflow_name] = workflow_data

# Write each workflow data to separate CSV files
for workflow_name, workflow_data in workflow_data_dict.items():
    csv_file = os.path.join(WORKFLOWS_FOLDER, f'{workflow_name}_workflow_steps_data.csv')
    with open(csv_file, mode='w', newline='') as file:
        fieldnames = ['Run ID', 'Run Name', 'Repository Name', 'Run Number', 'Run Attempt', 'Head Commit Message', 'Author', 'Job Name', 'Job Start Time', 'Job End Time', 'Job Status', 'Job Conclusion', 'Pull Request Number', 'Pull Request Title', 'Step Name', 'Status', 'Conclusion', 'Step Number', 'Started At', 'Completed At']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(workflow_data)

    print(f'Successfully captured workflow steps data for {workflow_name} in "{csv_file}".')

# Merge data from all workflow files into a single list
all_data = []
for workflow_data in workflow_data_dict.values():
    all_data.extend(workflow_data)

# Write all data to the final CSV file
csv_file = 'all_workflow_steps_data.csv'
with open(csv_file, mode='w', newline='') as file:
    fieldnames = ['Run ID', 'Run Name', 'Repository Name', 'Run Number', 'Run Attempt', 'Head Commit Message', 'Author', 'Job Name', 'Job Start Time', 'Job End Time', 'Job Status', 'Job Conclusion', 'Pull Request Number', 'Pull Request Title', 'Step Name', 'Status', 'Conclusion', 'Step Number', 'Started At', 'Completed At']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_data)

print(f'Successfully captured all workflow steps data from all workflow files in "{csv_file}".')

df = pd.DataFrame(all_data, columns=fieldnames)

    # Convert the 'Job Start Time' and 'Job End Time' columns to datetime
df['Job Start Time'] = pd.to_datetime(df['Job Start Time'])
df['Job End Time'] = pd.to_datetime(df['Job End Time'])

    # Extract the date from the 'Job Start Time' column and add it as a new column 'Date'
df['Date'] = df['Job Start Time'].dt.date

    # Group by 'Date', 'Run Name', 'Job Name', and 'Step Name', and get count of daily runs for each combination
pivot_table = df.groupby(['Date', 'Run Name', 'Job Name', 'Step Name', 'Job Conclusion']).size().unstack(fill_value=0)

    # Add 'Total' column to the pivot table to get the total count of runs for each combination
pivot_table['Total'] = pivot_table.sum(axis=1)
    # Create a DataFrame from the data
    #df = pd.DataFrame(all_data, columns=fieldnames)

    # Create a pivot table with the desired settings
    #pivot_table = df.pivot_table(index=['Run Name', 'Job Name','Step Name'], columns=['Job Conclusion'], aggfunc='size', fill_value=0)

    # Save the pivot table to a new CSV file
pivot_csv_file = 'pivot_table.csv'
pivot_table.to_csv(pivot_csv_file)
print(f'Successfully created the pivot table and saved it as "{pivot_csv_file}".')

summary = "Dynamic Sub-task: This is a test sub-task created via API"
description = "This is the description of the dynamic sub-task"
subtask_key = create_jira_subtask(PARENT_ISSUE_KEY, summary, description)


# Upload the report file as an attachment to the newly created issue
report_file_path = "all_workflow_steps_data.csv"  # Replace with the path to your report file
pivot_attachment_file_path = "pivot_table.csv"
upload_attachment_to_jira_issue(subtask_key, report_file_path)
upload_attachment_to_jira_issue(subtask_key, pivot_attachment_file_path)
