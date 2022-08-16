#!/bin/env python3

import sys
import os
import os.path

from gh_pr_creator.github import GithubClient, GH_TOKEN_ENV_NAME

HELP_MESSAGE = """
gh-pr-creator <message>

Создаёт PR на github для текущей ветки репозитория. Параметром передается message — сообщение, которое
будет добавлено в PR. Параметр обязателен.

Переменные окружения:

GH_TOKEN: токен авторизации в github API
"""

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


def main():
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