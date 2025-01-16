# backend/app/config.py

import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://myuser:mypassword@localhost:5432/contractdb")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
