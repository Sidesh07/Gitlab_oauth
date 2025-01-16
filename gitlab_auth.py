import os
import requests
from git import Repo
from dotenv import load_dotenv

load_dotenv(".env")

GITLAB_AUTH_URL = "https://gitlab.com/oauth/authorize"
GITLAB_TOKEN_URL = "https://gitlab.com/oauth/token"
GITLAB_API_URL = "https://gitlab.com/api/v4"

CLIENT_ID = os.getenv("GITLAB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITLAB_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GITLAB_REDIRECT_URI")

def get_gitlab_authorization_url():
    return f"{GITLAB_AUTH_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=read_user+read_api+api"

def exchange_code_for_token(code):
    response = requests.post(
        GITLAB_TOKEN_URL,
        headers={"Accept": "application/json"},
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        },
    )
    return response.json().get("access_token"), response.json().get("token_type") if response.status_code == 200 else (None, None)

def fetch_user_data(access_token):
    response = requests.get(f"{GITLAB_API_URL}/user", headers={"Authorization": f"Bearer {access_token}"})
    return response.json() if response.status_code == 200 else None

def fetch_user_repos(access_token):
    response = requests.get(f"{GITLAB_API_URL}/projects?owned=true", headers={"Authorization": f"Bearer {access_token}"})
    return response.json() if response.status_code == 200 else None

def fetch_user_organizations(access_token):
    response = requests.get(f"{GITLAB_API_URL}/groups", headers={"Authorization": f"Bearer {access_token}"})
    return [org["name"] for org in response.json()] if response.status_code == 200 else None

def clone_repo(repo_url, destination_folder, access_token):
    try:
        authenticated_url = repo_url.replace("https://gitlab.com", f"https://oauth2:{access_token}@gitlab.com")
        Repo.clone_from(authenticated_url, destination_folder)
        return {"status": "success", "message": f"Cloned {repo_url} to {destination_folder}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
