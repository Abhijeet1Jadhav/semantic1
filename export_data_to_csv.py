import os
import csv
from github import Github

# Get the GitHub token
token = os.getenv('RELEASE_GIT_TOKEN')
g = Github(token)
repo = g.get_repo('Abhijeet1Jadhav/semantic1')
# Get the path to the workflow file

workflow_file_path = '.github/workflows/extraction.yml'

# Read the workflow file
with open(workflow_file_path, 'r') as file:
    workflow_content = file.read()

# Extract step names and their status from the workflow content
steps = []
status = []
for line in workflow_content.splitlines():
    if 'name:' in line:
        steps.append(line.split('name:')[-1].strip())
    if 'conclusion:' in line:
        status.append(line.split('conclusion:')[-1].strip())

# Create a dictionary to store the information
data = {
    'Step': steps,
    'Status': status
}

# Create a DataFrame from the data dictionary
df = pd.DataFrame(data)

# Save the DataFrame to a CSV file
df.to_csv('step_status.csv', index=False)
