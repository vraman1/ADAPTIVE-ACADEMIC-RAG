import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

PG_CONN_STR = os.getenv(
    "PG_CONN_STR",
    "postgresql://postgres:postgres@localhost:5432/adaptive_rag"
)

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not set in the .env file."
    )