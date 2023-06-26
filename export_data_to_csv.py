import os
import csv
from github import Github

# Get the GitHub token
token = os.getenv('RELEASE_GIT_TOKEN')
g = Github(token)
repo = g.get_repo('Abhijeet1Jadhav/semantic1')
workflow_run = repo.get_workflow_runs()[0]
workflow_run_id = workflow_run.id

# Get the workflow run details
workflow_run_details = repo.get_workflow_run(workflow_run_id)

# Get the environment deployments status
#environment_deployments = workflow_run_details.get_environments()

# Get the step and job status
steps = workflow_run_details.get_steps()
jobs = workflow_run_details.get_jobs()

# Create a dictionary to store the information
data = {
    'Environment': [],
    'Deployment Status': [],
    'Step Status': [],
    'Job Status': []
}

# Process the environment deployments status
# for environment in environment_deployments:
    # data['Environment'].append(environment.environment)
    # data['Deployment Status'].append(environment.status)

# Process the step status
for step in steps:
    data['Step Status'].append(step.conclusion)

# Process the job status
for job in jobs:
    data['Job Status'].append(job.conclusion)

# Create a DataFrame from the data dictionary
df = pd.DataFrame(data)

# Save the DataFrame to a CSV file
df.to_csv('workflow_status.csv', index=False)
