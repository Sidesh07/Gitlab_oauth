import os
import base64
import json
from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv

load_dotenv(".env")

ENV_FILE = ".env"
TOKENS_FILE = "user_tokens.json"

def save_to_env_file(key, value):
    with open(ENV_FILE, "a+") as f:
        f.seek(0)
        if not any(line.startswith(f"{key}=") for line in f.readlines()):
            f.write(f"\n{key}={value}\n")

MASTER_KEY = os.getenv("MASTER_KEY")
if not MASTER_KEY:
    MASTER_KEY = base64.urlsafe_b64encode(os.urandom(32)).decode()
    save_to_env_file("MASTER_KEY", MASTER_KEY)

master_cipher = Fernet(MASTER_KEY)
ENCRYPTION_KEY = Fernet.generate_key().decode()
cipher = Fernet(ENCRYPTION_KEY)

def save_token(username, access_token):
    try:
        encrypted_token = cipher.encrypt(access_token.encode()).decode()
        if os.path.exists(TOKENS_FILE):
            with open(TOKENS_FILE, "r") as f:
                data = json.load(f)
        else:
            data = {}
        data[username] = encrypted_token
        with open(TOKENS_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error saving token: {e}")

def get_token(username):
    try:
        if os.path.exists(TOKENS_FILE):
            with open(TOKENS_FILE, "r") as f:
                data = json.load(f)
            encrypted_token = data.get(username)
            return cipher.decrypt(encrypted_token.encode()).decode() if encrypted_token else None
    except Exception as e:
        print(f"Error retrieving token: {e}")
        return None
