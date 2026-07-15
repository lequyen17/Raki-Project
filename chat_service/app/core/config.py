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
INTERNAL_API_TOKEN = "dev-secret-internal-token"

# ---------------------------------------------------------------------------
# Cloudflare R2 (S3-compatible) — điền các giá trị bên dưới vào .env
# ---------------------------------------------------------------------------
# R2_ACCOUNT_ID: Account ID trên Cloudflare dashboard (R2 > Overview)
# R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY: tạo tại R2 > Manage R2 API Tokens
# R2_BUCKET_NAME: tên bucket đã tạo
# R2_ENDPOINT_URL: https://<ACCOUNT_ID>.r2.cloudflarestorage.com
# R2_PUBLIC_URL: public URL của bucket (custom domain hoặc r2.dev public URL)
#                ví dụ: https://pub-xxxxx.r2.dev  hoặc  https://cdn.yourdomain.com
# ---------------------------------------------------------------------------
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID", "")  # TODO: điền Account ID
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID", "")  # TODO: điền Access Key ID
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY", "")  # TODO: điền Secret Access Key
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME", "")  # TODO: điền tên bucket
R2_ENDPOINT_URL = os.getenv("R2_ENDPOINT_URL", "")  # TODO: https://<ACCOUNT_ID>.r2.cloudflarestorage.com
R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL", "")  # TODO: public base URL để client tải file

# Giới hạn upload (bytes). Mặc định 50MB.
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", str(50 * 1024 * 1024)))
