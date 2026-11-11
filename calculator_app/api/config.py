import os

SERVE_FRONTEND = os.getenv("SERVE_FRONTEND", "false").lower() == "true"