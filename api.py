import os
import csv
import requests
import pandas as pd
from github import Github
import sys
from jira import JIRA
import base64
import time

JIRA_BASE_URL = 'https://demo-sw.atlassian.net'  # Replace with your Jira instance URL
JIRA_USERNAME = 'jadhavabhijeet6411@gmail.com'  # Replace with your Jira username
JIRA_API_TOKEN = 'ATATT3xFfGF02p9EeQx8J9wblId9urLXyHHB4csPlMFhvaendzPCDhYH1H1n-yUB5SSX3RnZsgDglteTdMLp6RfIMYMW0PHh3m9UxDIwFO7X9TUOtLrx6OPUnWhngo9m3VcBEydvzleCqEdUN3_yET9OLENewtTlx4SRldgBSgoDJmidHVYdoCg=AFC67CC0'  # Replace with your Jira API token
JIRA_PROJECT_KEY = 'DS'  # Replace with the ID of the Jira dashboard where you want to upload
PARENT_ISSUE_KEY = 'DS-2'  # Replace with the ID of the Jira dashboard where you want to upload

jira_credentials = (JIRA_USERNAME, JIRA_API_TOKEN)
jira = JIRA(server=JIRA_BASE_URL, basic_auth=jira_credentials)

def create_jira_subtask(parent_issue_key, summary, description, issue_type='Sub-task'):
    ticket_number = int(time.time())
    issue_dict = {
        'project': {'key': JIRA_PROJECT_KEY},
        'summary': f'{summary} ({ticket_number})',
        'description': description,
        'issuetype': {'name': issue_type},
        'parent': {'key': parent_issue_key}
    }
    new_issue = jira.create_issue(fields=issue_dict)
    return new_issue.key

def upload_attachment_to_jira_issue(issue_key, attachment_file_path):
    with open(attachment_file_path, 'rb') as file:
        jira.add_attachment(issue=issue_key, attachment=file)

# Replace with your personal access token
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']

# Replace with your repository details
REPO_OWNER = 'Abhijeet1Jadhav'
REPO_NAME = 'semantic1'
#WORKFLOW_FILE = 'extraction.yml'
WORKFLOWS_FOLDER = 'workflow_files'
#WORKFLOW_FILE = sys.argv[4]

# Set the headers including the access token
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

def get_deployment_count_per_environment(jobs):
    deployment_counts = {
        'Dev': 0,
        'Prod': 0,
        'QA': 0
    }

    for job_step in jobs:
        job_name = job_step['Job Name']
        if 'Deploy-to-Dev' in job_name and job_step['Job Conclusion'] == 'success':
            deployment_counts['Dev'] += 1
        elif 'Deploy to Prod' in job_name and job_step['Job Conclusion'] == 'success':
            deployment_counts['Prod'] += 1
        elif 'Deploy to QA' in job_name and job_step['Job Conclusion'] == 'success':
            deployment_counts['QA'] += 1

    return deployment_counts


# Replace with your GitHub repository details


# Connect to GitHub using the access token
g = Github(ACCESS_TOKEN)

# Fetch and store the enabled workflow names in a variable
repo = g.get_repo(f'{REPO_OWNER}/{REPO_NAME}')
workflows_folder = repo.get_contents('.github/workflows')
workflow_names_list = [file.name for file in workflows_folder if file.type == 'file']

# Create a dictionary to store data for each workflow file
workflow_data_dict = {}

total_deployment_counts = {
    'Dev': 0,
    'Prod': 0,
    'QA': 0
}

# Iterate over each workflow name and process its data
for workflow_name in workflow_names_list:
    workflow = repo.get_workflow(workflow_name)
    workflow_runs = workflow.get_runs()
    workflow_data = fetch_run_and_job_steps(workflow_name, workflow_runs)
    workflow_data_dict[workflow_name] = workflow_data

    # Get the deployment counts for this workflow and add them to the total counts
    deployment_counts = get_deployment_count_per_environment(workflow_data)
    for env, count in deployment_counts.items():
        total_deployment_counts[env] += count

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

# Generate deployment counts for each environment
#deployment_counts = get_deployment_count_per_environment(all_data)
#print(deployment_counts)

# Create a DataFrame from the data
df = pd.DataFrame(all_data, columns=fieldnames)

# Convert the 'Job Start Time' and 'Job End Time' columns to datetime
df['Job Start Time'] = pd.to_datetime(df['Job Start Time'])
df['Job End Time'] = pd.to_datetime(df['Job End Time'])

# Extract the date from the 'Job Start Time' column and add it as a new column 'Date'
df['Date'] = df['Job Start Time'].dt.date

# Group by 'Date', 'Run Name', 'Job Name', and 'Step Name', and get count of daily runs for each combination
pivot_table = df.groupby(['Date', 'Run Name', 'Job Name', 'Step Name', 'Job Conclusion']).size().unstack(fill_value=0)

# Add 'Total' column to the pivot table to get the total count of runs for each combination
pivot_table['Total Deployments'] = pivot_table.sum(axis=1)
#pivot_table['Total'] = total_deployment_counts
#for env, count in total_deployment_counts.items():
    #pivot_table[f'{env} Deployment'] = count

# Get the deployment counts for each environment	
#deployment_counts = get_deployment_count_per_environment(all_data)	
# Add deployment counts to the pivot table	
#for env, count in deployment_counts.items():	
    #pivot_table[f'{env} Deployments'] = count
# Create a DataFrame from the data	
#df_pivot_table = pd.DataFrame(pivot_table)

# Save the pivot table to a new CSV file
pivot_csv_file = 'pivot_table.csv'
pivot_table.to_csv(pivot_csv_file)
#pivot_table.to_csv(pivot_csv_file)
#df_pivot_table.to_csv(pivot_csv_file)

with open(pivot_csv_file, 'a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([])
    writer.writerow(['Dev Deployment', total_deployment_counts['Dev']])
    writer.writerow(['QA Deployment', total_deployment_counts['QA']])
    writer.writerow(['Prod Deployment', total_deployment_counts['Prod']])

print(f'Successfully created the pivot table and saved it as "{pivot_csv_file}".')

# Create Jira sub-task and upload reports as attachments
summary = "Dynamic Sub-task: This is a test sub-task created via API"
description = "This is the description of the dynamic sub-task"
subtask_key = create_jira_subtask(PARENT_ISSUE_KEY, summary, description)

# Upload the report file as an attachment to the newly created issue
report_file_path = "all_workflow_steps_data.csv"  # Replace with the path to your report file
pivot_attachment_file_path = "pivot_table.csv"
upload_attachment_to_jira_issue(subtask_key, report_file_path)
upload_attachment_to_jira_issue(subtask_key, pivot_attachment_file_path)
