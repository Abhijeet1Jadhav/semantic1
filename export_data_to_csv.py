import os
import csv
from github import Github

# Get the GitHub token
token = os.getenv('RELEASE_GIT_TOKEN')
g = Github(token)
repo = g.get_repo('Abhijeet1Jadhav/semantic1')
# Create a GitHub instance
#g = Github(token)

# Get the repository and pull request details
#repo = g.get_repo('Abhijeet1Jadhav/semantic1')  # Replace with your repository detailsd
pulls = repo.get_pulls(state='closed')  # Modify the pull request state as needed
latest_pull_request = pulls[0]  # Assumes the latest pull request is at index 0
# Get the head commit of the latest pull request
head_commit = latest_pull_request.head.sha

# Get the check runs for the head commit
check_runs = repo.get_commit(head_commit).get_check_runs()
# Prepare the data for CSV
data = [['Pull Request Number', 'Pull Request Title', 'Deployment Status', 'Workflow Step Status']]

for pull in pulls:
    # Get the deployment status for the pull request
    # Modify this logic to retrieve the correct deployment status based on your requirements
    deployment_status = 'Get deployment status here'

    # Get the workflow runs for the pull request
   # workflow_runs = pull.get_check_runs()
    workflow_runs = repo.get_commit(head_commit).get_check_runs()

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
