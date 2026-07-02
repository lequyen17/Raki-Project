import os

CHAT_DB_USER = os.getenv("CHAT_DB_USER", "chat_user")
CHAT_DB_PASSWORD = os.getenv("CHAT_DB_PASSWORD", "123456")
CHAT_DB_HOST = os.getenv("CHAT_DB_HOST", "chat-db")
CHAT_DB_PORT = os.getenv("CHAT_DB_PORT", "5432")
CHAT_DB_NAME = os.getenv("CHAT_DB_NAME", "chat_db")

DATABASE_URL = (
    f"postgresql://{CHAT_DB_USER}:{CHAT_DB_PASSWORD}"
    f"@{CHAT_DB_HOST}:{CHAT_DB_PORT}/{CHAT_DB_NAME}"
)

SECRET_KEY = "django-insecure-th-%d0roim2x$t-+inu!(v_eav@635=c30k*-=igvm$-uq_8jy"

JWT_ALGORITHM = "HS256"

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN", "dev-secret-internal-token")
