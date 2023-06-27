import os
from github import Github
import pandas as pd

def capture_statuses():
    statuses = []
    # Capture step statuses here and add them to the `statuses` list
    statuses.append(f"Step 1: {'success' if os.getenv('STEP1_STATUS') == 'success' else 'failure'}")
    statuses.append(f"Step 2: {'success' if os.getenv('STEP2_STATUS') == 'success' else 'failure'}")
    # Add more steps as needed

    # Save the statuses to a file
    with open('statuses.txt', 'w') as file:
        file.write('\n'.join(statuses))

if __name__ == '__main__':
    capture_statuses()
