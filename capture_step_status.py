import csv
import os
from github import Github
import pandas as pd

# Get the workflow run ID
workflow_run_id = str(os.getenv('GITHUB_EVENT_WORKFLOW_RUN_ID'))

# Get the GitHub token
token = os.getenv('GITHUB_TOKEN')

# Create a PyGithub instance
g = Github(token)

# Get the repository
repo = g.get_repo(os.getenv('GITHUB_REPOSITORY'))

# Get the workflow run details
workflow_run = repo.get_workflow_run(workflow_run_id)

# Get the step statuses
steps = workflow_run.get_steps()

# Create a list to store the step statuses
step_statuses = []

# Process the step statuses
for step in steps:
    step_statuses.append({
        'Step Name': step.name,
        'Status': step.conclusion
    })

# Create a DataFrame from the step statuses
df = pd.DataFrame(step_statuses)

# Save the DataFrame to a CSV file
df.to_csv('step_statuses.csv', index=False)
