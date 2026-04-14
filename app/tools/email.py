from app.config.log_config import logger

def send_email(to: str, subject: str, body: str) -> dict:
    logger.info(f"Sending email to {to}")
    return {
                "success": True,
                "data": {"status": "sent"},
                "error": None
            }