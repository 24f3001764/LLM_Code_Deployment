import os
import time
from pathlib import Path
from github import Github, GithubException
from src.config import config
from src.utils import sanitize_repo_name, get_mit_license
from src.security_scanner import SecurityScanner
import logging

logger = logging.getLogger(__name__)


class GitHubManager:
    """Manage GitHub repository creation and Pages deployment"""
    
    def __init__(self):
        self.github = Github(config.GITHUB_TOKEN)
        self.user = self.github.get_user()
        self.scanner = SecurityScanner()
    
    async def create_and_deploy(self, app_dir: Path, task_id: str) -> tuple[str, str, str]:
        """
        Create repo, push code, enable Pages
        Returns: (repo_url, commit_sha, pages_url)
        """
        repo_name = sanitize_repo_name(task_id)
        
        # Scan for secrets before deploying
        logger.info("Running security scan on generated code...")
        if not self.scanner.scan_and_report(app_dir):
            logger.warning("Secrets detected in code - deployment may contain sensitive information")
            # Note: We continue deployment but log the warning
            # In production, you might want to fail here or sanitize automatically
        
        # Check if repo exists, delete if it does (for testing/re-runs)
        try:
            existing_repo = self.user.get_repo(repo_name)
            logger.warning(f"Repo {repo_name} already exists, deleting...")
            existing_repo.delete()
            time.sleep(2)  # Wait for deletion to propagate
        except GithubException:
            pass  # Repo doesn't exist, which is what we want
        
        # Create new repository
        repo = self.user.create_repo(
            name=repo_name,
            description=f"Auto-generated app for task {task_id}",
            private=False,
            auto_init=False
        )
        
        logger.info(f"Created repo: {repo.html_url}")
        
        # Add LICENSE
        license_content = get_mit_license()
        repo.create_file(
            path="LICENSE",
            message="Add MIT License",
            content=license_content
        )
        
        # Add README.md
        readme_path = app_dir / "README.md"
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        repo.create_file(
            path="README.md",
            message="Add README",
            content=readme_content
        )
        
        # Add index.html
        index_path = app_dir / "index.html"
        with open(index_path, 'r', encoding='utf-8') as f:
            index_content = f.read()
        
        file_obj = repo.create_file(
            path="index.html",
            message="Add application",
            content=index_content
        )
        
        commit_sha = file_obj['commit'].sha
        
        # Enable GitHub Pages
        try:
            repo.create_pages_site(source={"branch": "main", "path": "/"})
            logger.info("GitHub Pages enabled")
        except GithubException as e:
            if "already exists" in str(e):
                logger.info("GitHub Pages already enabled")
            else:
                raise
        
        # Wait for Pages to be ready
        pages_url = f"https://{config.GITHUB_USERNAME}.github.io/{repo_name}/"
        
        # Give Pages time to deploy
        logger.info("Waiting for GitHub Pages to deploy...")
        time.sleep(10)
        
        return repo.html_url, commit_sha, pages_url
    
    async def update_repo(self, repo_name: str, app_dir: Path, update_message: str) -> tuple[str, str]:
        """
        Update existing repo with new code
        Returns: (commit_sha, pages_url)
        """
        # Scan for secrets before updating
        logger.info("Running security scan on updated code...")
        if not self.scanner.scan_and_report(app_dir):
            logger.warning("Secrets detected in updated code - deployment may contain sensitive information")
        
        repo = self.user.get_repo(repo_name)
        
        # Update README.md
        readme_path = app_dir / "README.md"
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        try:
            readme_file = repo.get_contents("README.md")
            repo.update_file(
                path="README.md",
                message=f"Update README: {update_message}",
                content=readme_content,
                sha=readme_file.sha
            )
        except GithubException:
            # File doesn't exist, create it
            repo.create_file(
                path="README.md",
                message="Add README",
                content=readme_content
            )
        
        # Update index.html
        index_path = app_dir / "index.html"
        with open(index_path, 'r', encoding='utf-8') as f:
            index_content = f.read()
        
        index_file = repo.get_contents("index.html")
        file_obj = repo.update_file(
            path="index.html",
            message=f"Update application: {update_message}",
            content=index_content,
            sha=index_file.sha
        )
        
        commit_sha = file_obj['commit'].sha
        pages_url = f"https://{config.GITHUB_USERNAME}.github.io/{repo_name}/"
        
        # Wait for Pages to redeploy
        logger.info("Waiting for GitHub Pages to redeploy...")
        time.sleep(10)
        
        return commit_sha, pages_url
