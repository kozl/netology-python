#!/bin/env python3

import sys
import os
import os.path

import requests

HELP_MESSAGE = """
gh-pr-creator <message>

Создаёт PR на github для текущей ветки репозитория. Параметром передается message — сообщение, которое
будет добавлено в PR. Параметр обязателен.

Переменные окружения:

GH_TOKEN: токен авторизации в github API
"""

GH_TOKEN_ENV_NAME = "GH_TOKEN"
GH_USER = "kozl"

class GithubClient:
    def __init__(self, token: str) -> None:
        session = requests.Session()
        session.headers.update({"Accept": "application/vnd.github.v3+json"})
        session.auth = (GH_USER, token)

        self.session = session
        self.api_url = "https://api.github.com"

    def _get(self, path: str) -> requests.Response:
        return self.session.get(f"{self.api_url}/{path}")

    def _post(self, path: str, payload: dict) -> requests.Response:
        return self.session.post(f"{self.api_url}/{path}", json=payload)

    def is_repo_exists(self, repo_name: str) -> bool:
        """
        Проверяет, что локальный репозиторий существует на github
        """
        resp = self._get(f"repos/{GH_USER}/{repo_name}")
        return resp.ok
    
    def create_pr(self, repo_name: str, branch: str, message: str) -> str:
        """
        Создаёт PR текущей ветки в master и возвращает url на него
        """
        resp = self._post(
            f"repos/{GH_USER}/{repo_name}/pulls",
            payload={
                "title": message,
                "head": branch,
                "base": "master",
            },
            )
        response_dto = resp.json()
        if not resp.ok:
            raise Exception(f"status code: {resp.status_code}, body: {response_dto}")
        return response_dto["html_url"]

def is_repo() -> bool:
    """
    Возвращает true, если текущая директория является git репозиторием
    """
    if os.path.isdir(os.path.join(os.getcwd(), ".git")):
        return True
    return False

def current_branch() -> str:
    with open('.git/HEAD') as f:
        return f.read().strip().split('/')[-1]

def fatal(msg: str):
    print(msg)
    sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        fatal(HELP_MESSAGE)
    
    if not is_repo():
        fatal("Текущая директория не является git репозиторием")
    
    if not os.environ.get(GH_TOKEN_ENV_NAME, None):
        fatal(f"Переменная окружения {GH_TOKEN_ENV_NAME} не установлена")

    gh_client = GithubClient(os.environ.get(GH_TOKEN_ENV_NAME))
    repo_name = os.path.basename(os.getcwd())
    if not gh_client.is_repo_exists(repo_name):
        fatal("Текущий репозиторий не найден на github")

    try:
        url = gh_client.create_pr(repo_name, current_branch(), sys.argv[1])
    except Exception as e:
        fatal(f"Произошла ошибка: {e}")

    print(f"Ссылка на PR: {url}")