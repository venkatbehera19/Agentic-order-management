def send_email(to: str, subject: str, body: str) -> dict:
    print(f"Sending email to {to}")
    return {"status": "sent"}