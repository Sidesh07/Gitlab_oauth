from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from gitlab import gitlab_oauth_api

app = Flask(__name__)
CORS(app, resources={r"/gitlab/*": {"origins": "http://localhost:3000"}})

api = Api(app)
api.add_namespace(gitlab_oauth_api, path="/gitlab")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
