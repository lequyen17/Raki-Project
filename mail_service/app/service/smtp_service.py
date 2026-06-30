"""
SMTP Service — Gửi các loại email của Raki qua SMTP.

Cấu hình qua biến môi trường:
  SMTP_HOST       : SMTP server host        (default: smtp.gmail.com)
  SMTP_PORT       : SMTP port               (default: 587)
  SMTP_USER       : Địa chỉ email gửi đi
  SMTP_PASSWORD   : App password của SMTP
  FROM_EMAIL      : Tên hiển thị + email    (default: "Raki App <{SMTP_USER}>")
"""

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cấu hình SMTP từ biến môi trường
# ---------------------------------------------------------------------------
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "halequyen1725@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "zuqo umap whyj yfgk")
FROM_EMAIL = os.getenv("FROM_EMAIL", f"Raki App <{SMTP_USER}>")


# ---------------------------------------------------------------------------
# Hàm gửi mail nội bộ
# ---------------------------------------------------------------------------

def _send(to: str, subject: str, text_body: str, html_body: str) -> None:
    """Gửi email qua SMTP với cả plain text và HTML."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to

    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, [to], msg.as_string())

    logger.info("Email sent to %s | subject: %s", to, subject)


# ---------------------------------------------------------------------------
# Các template email
# ---------------------------------------------------------------------------

def send_otp_email(to: str, otp: str, first_name: str = "bạn") -> None:
    """Gửi email chứa mã OTP xác thực đăng ký."""
    subject = "Mã OTP xác thực đăng ký Raki"

    text_body = (
        f"Xin chào {first_name},\n\n"
        f"Mã OTP xác thực tài khoản của bạn là: {otp}\n\n"
        f"Mã có hiệu lực trong 5 phút. Vui lòng không chia sẻ mã này với ai.\n\n"
        f"Trân trọng,\nĐội ngũ Raki"
    )

    html_body = f"""
    <div style="font-family:Inter,Arial,sans-serif;max-width:560px;margin:auto;padding:32px 24px;
                background:#ffffff;border-radius:12px;border:1px solid #e5e7eb;">
      <h2 style="color:#1e293b;margin-bottom:8px;">Xin chào {first_name}! 👋</h2>
      <p style="color:#475569;">Cảm ơn bạn đã đăng ký tài khoản trên <strong>Raki</strong>.</p>
      <p style="color:#475569;">Mã OTP xác thực của bạn là:</p>
      <div style="font-size:36px;font-weight:700;letter-spacing:12px;
                  background:#f0f4ff;padding:20px 28px;border-radius:10px;
                  display:inline-block;margin:16px 0;color:#3b82f6;
                  border:1px solid #bfdbfe;">
        {otp}
      </div>
      <p style="color:#475569;">Mã có hiệu lực trong <strong>5 phút</strong>.</p>
      <p style="color:#94a3b8;font-size:13px;">Vui lòng không chia sẻ mã này với bất kỳ ai.</p>
      <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;">
      <p style="color:#64748b;font-size:13px;">Trân trọng,<br><strong>Đội ngũ Raki</strong></p>
    </div>
    """

    _send(to, subject, text_body, html_body)


def send_welcome_email(to: str, username: str, full_name: str) -> None:
    """Gửi email chào mừng sau khi đăng ký thành công."""
    subject = "Chào mừng bạn đến với Raki! 🎉"

    text_body = (
        f"Xin chào {full_name},\n\n"
        f"Tài khoản của bạn đã được tạo thành công trên Raki.\n"
        f"Tên đăng nhập: {username}\n\n"
        f"Bắt đầu học ngay và chinh phục mọi bộ flashcard của bạn!\n\n"
        f"Trân trọng,\nĐội ngũ Raki"
    )

    html_body = f"""
    <div style="font-family:Inter,Arial,sans-serif;max-width:560px;margin:auto;padding:32px 24px;
                background:#ffffff;border-radius:12px;border:1px solid #e5e7eb;">
      <h2 style="color:#1e293b;margin-bottom:8px;">Chào mừng, {full_name}! 🎉</h2>
      <p style="color:#475569;">
        Tài khoản của bạn đã được tạo thành công trên <strong>Raki</strong>.
      </p>
      <table style="margin:16px 0;border-collapse:collapse;">
        <tr>
          <td style="color:#64748b;padding:6px 12px 6px 0;font-size:14px;">Tên đăng nhập:</td>
          <td style="color:#1e293b;font-weight:600;font-size:14px;">{username}</td>
        </tr>
        <tr>
          <td style="color:#64748b;padding:6px 12px 6px 0;font-size:14px;">Email:</td>
          <td style="color:#1e293b;font-weight:600;font-size:14px;">{to}</td>
        </tr>
      </table>
      <p style="color:#475569;">Bắt đầu học ngay và chinh phục mọi bộ flashcard của bạn! 📚</p>
      <a href="#" style="display:inline-block;margin-top:8px;padding:12px 28px;
                         background:#3b82f6;color:#fff;text-decoration:none;
                         border-radius:8px;font-weight:600;font-size:15px;">
        Vào học ngay
      </a>
      <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;">
      <p style="color:#64748b;font-size:13px;">Trân trọng,<br><strong>Đội ngũ Raki</strong></p>
    </div>
    """

    _send(to, subject, text_body, html_body)


def send_review_reminder_email(to: str, first_name: str) -> None:
    """Gửi email nhắc nhở ôn tập flashcard hàng ngày."""
    name = first_name or "bạn"
    subject = "📚 Đừng quên ôn tập flashcard hôm nay!"

    text_body = (
        f"Xin chào {name},\n\n"
        f"Bạn có thẻ flashcard đang chờ ôn tập hôm nay.\n"
        f"Hãy dành vài phút để ôn lại — kiến thức sẽ ghi nhớ lâu hơn!\n\n"
        f"Trân trọng,\nĐội ngũ Raki"
    )

    html_body = f"""
    <div style="font-family:Inter,Arial,sans-serif;max-width:560px;margin:auto;padding:32px 24px;
                background:#ffffff;border-radius:12px;border:1px solid #e5e7eb;">
      <h2 style="color:#1e293b;margin-bottom:8px;">Xin chào {name}! 📚</h2>
      <p style="color:#475569;font-size:15px;line-height:1.6;">
        Bạn có <strong style="color:#3b82f6;">thẻ flashcard đang chờ ôn tập</strong> hôm nay.
      </p>
      <p style="color:#475569;font-size:15px;line-height:1.6;">
        Hãy dành vài phút để ôn lại — kiến thức được ôn đúng lúc sẽ ghi nhớ lâu hơn rất nhiều!
      </p>
      <div style="background:#f0f9ff;border-left:4px solid #3b82f6;padding:16px 20px;
                  border-radius:0 8px 8px 0;margin:20px 0;">
        <p style="margin:0;color:#1e40af;font-size:14px;font-weight:500;">
          💡 Mẹo: Chỉ cần 10–15 phút mỗi ngày là đủ để duy trì kiến thức hiệu quả.
        </p>
      </div>
      <a href="#" style="display:inline-block;margin-top:8px;padding:12px 28px;
                         background:#3b82f6;color:#fff;text-decoration:none;
                         border-radius:8px;font-weight:600;font-size:15px;">
        Ôn tập ngay
      </a>
      <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;">
      <p style="color:#64748b;font-size:13px;">Trân trọng,<br><strong>Đội ngũ Raki</strong></p>
      <p style="color:#94a3b8;font-size:12px;margin-top:8px;">
        Bạn nhận được email này vì tài khoản Raki của bạn có thẻ cần ôn tập.
      </p>
    </div>
    """

    _send(to, subject, text_body, html_body)
