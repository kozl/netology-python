import requests

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