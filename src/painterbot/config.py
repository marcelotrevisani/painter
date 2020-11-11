import os


PORT = int(os.environ.get("PORT", 8080))
REPO = os.environ.get("REPO")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")
GH_USERNAME = os.environ.get("GH_USERNAME")
GH_AUTH = os.environ.get("GH_AUTH")
GH_AUTH_BOT = os.environ.get("GH_AUTH_BOT")
GH_SECRET = os.environ.get("GH_SECRET")

