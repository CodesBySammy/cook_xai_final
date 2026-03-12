import requests
from core.config import settings
from core.logger import logger

class GitHubClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {settings.GITHUB_TOKEN}" if settings.GITHUB_TOKEN else ""
        })

    def get_pr_files(self, repo_name: str, pr_number: int) -> list:
        url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}/files"
        res = self.session.get(url)
        if res.status_code == 200:
            return res.json()
        logger.error(f"Error fetching PR files: {res.status_code}")
        return []

    def fetch_raw_code(self, raw_url: str) -> str:
        res = self.session.get(raw_url)
        return res.text if res.status_code == 200 else ""

    def post_comment(self, repo_name: str, pr_number: int, body: str):
        url = f"https://api.github.com/repos/{repo_name}/issues/{pr_number}/comments"
        res = self.session.post(url, json={"body": body})
        if res.status_code == 201:
            logger.info(f"Review posted to PR #{pr_number}")
        else:
            logger.error(f"Failed to post comment: {res.text}")

    def set_status_check(self, repo_name: str, sha: str, state: str, description: str):
        url = f"https://api.github.com/repos/{repo_name}/statuses/{sha}"
        payload = {
            "state": state, # 'success', 'failure', 'pending'
            "description": description[:140],
            "context": "XAI PR Gatekeeper"
        }
        res = self.session.post(url, json=payload)
        logger.info(f"Status check '{state}' set for commit {sha[:7]}")

github_api = GitHubClient()