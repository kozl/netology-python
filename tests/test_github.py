from requests_mock import Mocker
import pytest
from gh_pr_creator.github import GithubClient, GH_USER

def test_github_is_repo_exists_success():
    gh = GithubClient(token="deadbeef")
    with Mocker() as m:
        m.get(f'https://api.github.com/repos/{GH_USER}/testrepo', status_code=200)
        assert gh.is_repo_exists("testrepo")

def test_github_is_repo_exists_fails():
    gh = GithubClient(token="deadbeef")
    with Mocker() as m:
        m.get(f'https://api.github.com/repos/{GH_USER}/testrepo', status_code=404)
        assert not gh.is_repo_exists("testrepo")

def test_github_create_pr_success():
    gh = GithubClient(token="deadbeef")
    with Mocker() as m:
        m.post(f'https://api.github.com/repos/{GH_USER}/testrepo/pulls', status_code=200, json={"html_url": "http://my-pull-request"})
        url = gh.create_pr("testrepo", "branch", "message")
        assert url == "http://my-pull-request"