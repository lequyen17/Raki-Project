"""
Mail Service — FastAPI app

Endpoints:
  POST /mail/otp              — Gửi email OTP xác thực đăng ký
  POST /mail/welcome          — Gửi email chào mừng sau đăng ký
  POST /mail/review-reminder  — Gửi email nhắc ôn tập (dùng cho trigger thủ công)

Scheduler:
  Hàng ngày lúc 08:00 ICT (01:00 UTC) tự động:
    1. Gọi GET {BACKEND_URL}/api/users/review-due/ với header X-Internal-Token
    2. Gửi review reminder email tới từng user trong danh sách trả về
"""

import logging
import os

import httpx
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

from app.service.smtp_service import (
    send_otp_email,
    send_review_reminder_email,
    send_welcome_email,
)

# ---------------------------------------------------------------------------
# Cấu hình
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

BACKEND_URL = "http://backend:8000"
INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN", "dev-secret-internal-token")


# ---------------------------------------------------------------------------
# Pydantic request schemas
# ---------------------------------------------------------------------------

class OtpEmailRequest(BaseModel):
    to: EmailStr
    otp: str
    first_name: str = "bạn"


class WelcomeEmailRequest(BaseModel):
    to: EmailStr
    username: str
    full_name: str


class ReviewReminderRequest(BaseModel):
    to: EmailStr
    first_name: str = "bạn"


# ---------------------------------------------------------------------------
# Daily scheduler job
# ---------------------------------------------------------------------------

def send_daily_review_reminders() -> None:
    """
    Job chạy hàng ngày:
    1. Gọi backend API lấy danh sách users có card cần ôn tập.
    2. Gửi email nhắc nhở tới từng user.
    """
    logger.info("=== Daily review reminder job started ===")
    url = f"{BACKEND_URL}/api/users/review-due/"
    headers = {"X-Internal-Token": INTERNAL_API_TOKEN}

    try:
        response = httpx.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        users = response.json().get("users", [])
        logger.info("Found %d users with due cards", len(users))
    except Exception as exc:
        logger.error("Failed to fetch due users from backend: %s", exc)
        return

    success_count = 0
    fail_count = 0

    for user in users:
        email = user.get("email", "")
        first_name = user.get("first_name", "")
        username = user.get("username", "")

        if not email:
            continue

        try:
            send_review_reminder_email(
                to=email,
                first_name=first_name or username,
            )
            success_count += 1
        except Exception as exc:
            logger.error("Failed to send reminder to %s: %s", email, exc)
            fail_count += 1

    logger.info(
        "=== Daily reminder done | sent: %d | failed: %d ===",
        success_count,
        fail_count,
    )


# ---------------------------------------------------------------------------
# FastAPI lifespan — khởi tạo & dừng scheduler
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(application: FastAPI):
    scheduler = BackgroundScheduler(timezone="Asia/Ho_Chi_Minh")
    # Chạy lúc 08:00 SA giờ Việt Nam (ICT = UTC+7)
    scheduler.add_job(
        send_daily_review_reminders,
        trigger=CronTrigger(hour=8, minute=0),
        id="daily_review_reminder",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started — daily review reminder at 08:00 ICT")
    yield
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Raki Mail Service",
    description="Microservice gửi email cho hệ thống Raki",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["Health"])
def health_check():
    """Kiểm tra trạng thái mail service."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Email endpoints
# ---------------------------------------------------------------------------

@app.post("/mail/otp", tags=["Mail"], summary="Gửi OTP email")
def mail_otp(body: OtpEmailRequest):
    """Gửi email chứa mã OTP xác thực đăng ký."""
    try:
        send_otp_email(to=body.to, otp=body.otp, first_name=body.first_name)
        return {"success": True, "message": "OTP email sent"}
    except Exception as exc:
        logger.error("send_otp_email error: %s", exc)
        raise HTTPException(status_code=500, detail="MAIL_SEND_FAILED")


@app.post("/mail/welcome", tags=["Mail"], summary="Gửi Welcome email")
def mail_welcome(body: WelcomeEmailRequest):
    """Gửi email chào mừng sau khi đăng ký thành công."""
    try:
        send_welcome_email(
            to=body.to,
            username=body.username,
            full_name=body.full_name,
        )
        return {"success": True, "message": "Welcome email sent"}
    except Exception as exc:
        logger.error("send_welcome_email error: %s", exc)
        raise HTTPException(status_code=500, detail="MAIL_SEND_FAILED")


@app.post("/mail/review-reminder", tags=["Mail"], summary="Gửi Review Reminder email")
def mail_review_reminder(body: ReviewReminderRequest):
    """Gửi email nhắc ôn tập thủ công cho một user cụ thể."""
    try:
        send_review_reminder_email(to=body.to, first_name=body.first_name)
        return {"success": True, "message": "Review reminder email sent"}
    except Exception as exc:
        logger.error("send_review_reminder_email error: %s", exc)
        raise HTTPException(status_code=500, detail="MAIL_SEND_FAILED")


# @app.post(
#     "/mail/trigger-daily-reminder",
#     tags=["Internal"],
#     summary="[Internal] Trigger daily reminder job thủ công",
# )
# def trigger_daily_reminder():
#     """
#     Chạy ngay daily reminder job (dùng để test mà không cần đợi đến 8h sáng).
#     """
#     try:
#         send_daily_review_reminders()
#         return {"success": True, "message": "Daily reminder job triggered"}
#     except Exception as exc:
#         logger.error("trigger_daily_reminder error: %s", exc)
#         raise HTTPException(status_code=500, detail="JOB_FAILED")
