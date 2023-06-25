const { Octokit } = require("@octokit/rest");
const { createReadStream, createWriteStream } = require("fs");
const parse = require("csv-parse");
const stringify = require("csv-stringify");

// GitHub API token
const token = process.env.GITHUB_TOKEN;

// Repository owner and name
const owner = "Abhijeet1Jadhav;
const repo = "semantic1;

// Path to the CSV report file
const reportPath = "report.csv";

// Initialize Octokit
const octokit = new Octokit({ auth: token });

// Fetch pull request details, environment deployment status, and workflow step status
async function fetchData() {
  try {
    // Fetch closed pull requests
    const { data: pullRequests } = await octokit.pulls.list({
      owner,
      repo,
      state: "closed",
    });

    // Fetch deployment statuses for each closed pull request
    const deployments = [];
    for (const pr of pullRequests) {
      const { data: deployment } = await octokit.repos.listDeployments({
        owner,
        repo,
        ref: pr.merge_commit_sha,
        task: "deploy",
        environment: "dev",
      });

      deployments.push(deployment);
    }

    // Fetch workflow run statuses for each closed pull request
    const workflowSteps = [];
    for (const pr of pullRequests) {
      const { data: workflowRuns } = await octokit.actions.listWorkflowRunsForRepo({
        owner,
        repo,
        branch: pr.head.ref,
      });

      for (const run of workflowRuns.workflow_runs) {
        const { data: workflowRun } = await octokit.actions.getWorkflowRun({
          owner,
          repo,
          run_id: run.id,
        });

        workflowSteps.push(workflowRun.steps);
      }
    }

    // Combine the data into a single array
    const reportData = [];
    for (let i = 0; i < pullRequests.length; i++) {
      const pr = pullRequests[i];
      const deployment = deployments[i];
      const workflowRun = workflowSteps[i];

      const row = {
        pullRequestId: pr.id,
        pullRequestTitle: pr.title,
        deploymentStatus: deployment.length > 0 ? deployment[0].state : "Not deployed",
        workflowStepStatus: workflowRun.map(step => step.conclusion).join(", "),
      };

      reportData.push(row);
    }

    return reportData;
  } catch (error) {
    console.error("Error fetching data:", error);
    throw error;
  }
}

// Generate the CSV report
async function generateCSVReport() {
  try {
    const reportData = await fetchData();

    // Create the CSV writer
    const csvWriter = stringify({
      header: true,
      columns: ["Pull Request ID", "Pull Request Title", "Deployment Status", "Workflow Step Status"],
    });

    // Write the report data to the CSV file
    const writeStream = createWriteStream(reportPath);
    csvWriter.pipe(writeStream);
    for (const row of reportData) {
      csvWriter.write(row);
    }
    csvWriter.end();

    console.log(`CSV report generated at ${reportPath}`);
  } catch (error) {
    console.error("Error generating CSV report:", error);
    process.exit(1);
  }
}

generateCSVReport();
