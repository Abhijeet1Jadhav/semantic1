const fs = require('fs');
const { Octokit } = require('@octokit/rest');

const octokit = new Octokit();

async function generateCSV() {
  const owner = 'Abhijeet1Jadhav';
  const repo = 'https://github.com/Abhijeet1Jadhav/semantic1.git';

  const { data: pullRequests } = await octokit.pulls.list({
    owner,
    repo,
  });

  const csvContent = pullRequests
    .map(pr => `${pr.number},${pr.title},${pr.user.login}`)
    .join('\n');

  fs.writeFileSync('pull_requests.csv', csvContent);
}

generateCSV().catch(console.error);
