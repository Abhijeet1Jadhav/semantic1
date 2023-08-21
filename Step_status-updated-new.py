# Import necessary libraries
import os
import csv
import requests
import pandas as pd
from github import Github
from jira import JIRA
import base64
import time
import sys

# Jira configuration
#JIRA_BASE_URL = 'https://demo-sw.atlassian.net'
#JIRA_USERNAME = 'jadhavabhijeet6411@gmail.com'
#JIRA_API_TOKEN = os.environ['JIRA_ACCESS_TOKEN']  # Replace with your Jira API token
#JIRA_PROJECT_KEY = 'TES'
#PARENT_ISSUE_KEY = 'TES-1'

# Create Jira connection
#jira_credentials = (JIRA_USERNAME, JIRA_API_TOKEN)
#jira = JIRA(server=JIRA_BASE_URL, basic_auth=jira_credentials)

# Function to create a Jira sub-task
#def create_jira_subtask(parent_issue_key, summary, description, issue_type='Sub-task'):
   # ticket_number = int(time.time())
    #issue_dict = {
     #   'project': {'key': JIRA_PROJECT_KEY},
      #  'summary': f'{summary} ({ticket_number})',
       # 'description': description,
        #'issuetype': {'name': issue_type},
        #'parent': {'key': parent_issue_key},
        #'components': [{'name': 'Release Management PoC'}]  # Add the component name here
    #}
    #new_issue = jira.create_issue(fields=issue_dict)
    #return new_issue.key

# Function to upload attachment to a Jira issue
#def upload_attachment_to_jira_issue(issue_key, attachment_file_path):
 #   with open(attachment_file_path, 'rb') as file:
  #      jira.add_attachment(issue=issue_key, attachment=file)

# GitHub configuration
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']  # Replace with your personal access token
WORKFLOWS_FOLDER = 'workflow_files'
headers = {
    'Authorization': f'token {ACCESS_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

# List of repository details
REPO_DETAILS_LIST = [
    {'owner': 'Abhijeet1Jadhav', 'name': 'semantic1'},
    {'owner': 'Abhijeet1Jadhav', 'name': 'demorelease'}
    # Add more repository details as needed
]

# Function to fetch run and job steps from GitHub
def fetch_run_and_job_steps(repo_owner, repo_name, workflow_name, workflow_runs):
    run_and_job_steps = []

    for workflow_run in workflow_runs:
        run_id = workflow_run.id

        # Make a GET request to retrieve job details for the workflow run
        api_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/actions/runs/{run_id}/jobs'
        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            jobs = response.json()['jobs']

            for job in jobs:
                # Extract job and step details here
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
                    conclusion = step.get('conclusion', None)
                    step_number = step['number']
                    started_at = step['started_at']
                    completed_at = step['completed_at']

                    # Create a dictionary for the job and step details
                    job_step_data = {
                        'Run ID': run_id,
                        'Run Name': workflow_name,
                        'Repository Name': f'{repo_owner}/{repo_name}',
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
                    }
                    
                    # Append the job and step data to the list
                    run_and_job_steps.append(job_step_data)

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

# Read repository names from command line arguments
repo_names = sys.argv[1:]

# Create a list to store all data
all_data = []

unique_timestamps = {}

# Create dictionaries to store deployment counts for each repository and environment
total_deployment_counts = {
    'Dev': 0,
    'Prod': 0,
    'QA': 0
}

repo_deployment_counts = {}

# Loop through each repository
for repo_name in repo_names:
    REPO_OWNER, REPO_NAME = repo_name.split('/')
    print(f'Fetching data for repository: {REPO_NAME}...')

    # Connect to GitHub using the access token
    g = Github(ACCESS_TOKEN)

    repo = g.get_repo(f'{REPO_OWNER}/{REPO_NAME}')
    workflows_folder = repo.get_contents('.github/workflows')
    workflow_names_list = [file.name for file in workflows_folder if file.type == 'file']

    # Iterate over each workflow name and process its data
    for workflow_name in workflow_names_list:
        workflow = repo.get_workflow(workflow_name)
        workflow_runs = workflow.get_runs()
        workflow_data = fetch_run_and_job_steps(REPO_OWNER, REPO_NAME, workflow_name, workflow_runs)

        # Append the workflow data to the all_data list
        all_data.extend(workflow_data)

df = pd.DataFrame(all_data)

# Create a dictionary to store unique job information
unique_jobs = {}

# Iterate through the DataFrame to populate the unique_jobs dictionary
for index, row in df.iterrows():
    job_key = (row['Job Name'], row['Job Start Time'])
    if job_key not in unique_jobs:
        unique_jobs[job_key] = {'Job Status': row['Job Status'], 'Job Conclusion': row['Job Conclusion']}

# Update the 'Job Status' and 'Job Conclusion' columns in the DataFrame
df['Job Status'] = df.apply(lambda row: unique_jobs[(row['Job Name'], row['Job Start Time'])]['Job Status'], axis=1)
df['Job Conclusion'] = df.apply(lambda row: unique_jobs[(row['Job Name'], row['Job Start Time'])]['Job Conclusion'], axis=1)

# Group by 'Job Start Time', 'Repository Name', 'Run Name', 'Job Name', and 'Job Status',
# and get count of job statuses for each combination
pivot_table = df.groupby(['Job Start Time', 'Repository Name', 'Run Name', 'Job Name', 'Job Status']).size().unstack(fill_value=0)

# Sum the job statuses to get the total count of unique jobs with each status
pivot_table['Total'] = pivot_table.sum(axis=1)

# Save the pivot table to a CSV file
pivot_csv_file = 'pivot_table.csv'
pivot_table.to_csv(pivot_csv_file)

print(f'Successfully created the pivot table and saved it as "{pivot_csv_file}".')

with open(pivot_csv_file, 'a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([])
    writer.writerow(['Dev Deployment', total_deployment_counts['Dev']])
    writer.writerow(['QA Deployment', total_deployment_counts['QA']])
    writer.writerow(['Prod Deployment', total_deployment_counts['Prod']])

print(f'Successfully created the pivot table and saved it as "{pivot_csv_file}".')

#print(f'Successfully created the pivot table and saved it as "{pivot_csv_file}".')

# Create Jira sub-task and upload reports as attachments
#summary = "Dynamic Sub-task: This is a test sub-task created via API"
#description = "This is the description of the dynamic sub-task"
#subtask_key = create_jira_subtask(PARENT_ISSUE_KEY, summary, description)

# Upload the report file as an attachment to the newly created issue
#report_file_path = "all_workflow_steps_data.csv"  # Replace with the path to your report file
#pivot_attachment_file_path = "pivot_table.csv"
#upload_attachment_to_jira_issue(subtask_key, report_file_path)
#upload_attachment_to_jira_issue(subtask_key, pivot_attachment_file_path)
