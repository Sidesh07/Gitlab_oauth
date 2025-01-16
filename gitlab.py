from flask import request, jsonify, redirect
from flask_restx import Namespace, Resource
from gitlab_auth import (
    get_gitlab_authorization_url,
    exchange_code_for_token,
    fetch_user_data,
    fetch_user_repos,
    fetch_user_organizations,
    clone_repo,
)
from token_manager import save_token, get_token

gitlab_oauth_api = Namespace("oauth", description="GitLab OAuth Integration")

@gitlab_oauth_api.route("/authorize")
class GitLabAuthorize(Resource):
    def get(self):
        """Redirect to GitLab for user authorization."""
        auth_url = get_gitlab_authorization_url()
        return redirect(auth_url)

@gitlab_oauth_api.route("/callback")
class GitLabCallback(Resource):
    def get(self):
        """Handle GitLab callback, process repositories, organizations, and clone repos."""
        code = request.args.get("code")
        if not code:
            return {"error": "Code parameter is missing"}, 400

        access_token, token_type = exchange_code_for_token(code)
        if not access_token:
            return {"error": "Failed to get access token"}, 400

        repositories = fetch_user_repos(access_token)
        if repositories is None:
            return {"error": "Failed to fetch repositories"}, 400

        user_data = fetch_user_data(access_token)
        if not user_data:
            return {"error": "Failed to fetch user data"}, 400

        organizations = fetch_user_organizations(access_token)
        username = user_data.get("username")

        save_token(username, access_token)

        # Display repositories for user selection
        print("\nRepositories Available:")
        for index, repo in enumerate(repositories, start=1):
            print(f"{index}. {repo['name']} - {repo['http_url_to_repo']}")

        selected_index = int(input("\nSelect a repository to clone (Enter the number): ")) - 1
        if selected_index < 0 or selected_index >= len(repositories):
            return {"error": "Invalid repository selection"}, 400

        selected_repo = repositories[selected_index]
        clone_result = clone_repo(
            selected_repo["http_url_to_repo"],
            f"./cloned_repos/{username}/{selected_repo['name']}",
            access_token
        )

        return jsonify({
            "repository_cloned": selected_repo["name"],
            "clone_status": clone_result["status"],
            "clone_message": clone_result["message"],
            "repositories": [{"name": repo["name"], "url": repo["http_url_to_repo"]} for repo in repositories],
            "organizations": organizations,
            "user_details": user_data,
        })
