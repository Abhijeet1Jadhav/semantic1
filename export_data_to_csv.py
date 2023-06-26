import os
import csv
from github import Github

# Get the GitHub token
token = os.environ['GITHUB_TOKEN']

# Create a GitHub instance
g = Github(token)

# Get the repository and pull request details
repo = g.get_repo('Abhijeet1Jadhav/semantic1')  # Replace with your repository details
pulls = repo.get_pulls(state='closed')  # Modify the pull request state as needed

# Prepare the data for CSV
data = [['Pull Request Number', 'Pull Request Title', 'Deployment Status', 'Workflow Step Status']]

for pull in pulls:
    # Get the deployment status for the pull request
    # Modify this logic to retrieve the correct deployment status based on your requirements
    deployment_status = 'Get deployment status here'

    # Get the workflow runs for the pull request
    workflow_runs = pull.get_check_runs()

    # Loop through each workflow run and get the step status
    for run in workflow_runs:
        # Modify this logic to retrieve the correct step status based on your requirements
        step_status = 'Get step status here'

        # Append the data to the list
        data.append([pull.number, pull.title, deployment_status, step_status])

# Export data to CSV
csv_file_name = sys.argv[1]
with open(csv_file_name, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(data)
