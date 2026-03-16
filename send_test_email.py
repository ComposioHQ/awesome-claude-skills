import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SENDER_EMAIL = "makladmk87@gmail.com"
APP_PASSWORD  = "pzbk rryf zhsw vllu"
RECIPIENT     = "dt23082411@gmail.com"

msg = MIMEMultipart()
msg["From"]    = SENDER_EMAIL
msg["To"]      = RECIPIENT
msg["Subject"] = "Test Email"

msg.attach(MIMEText("This is a test email sent via Python SMTP.", "plain"))

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(SENDER_EMAIL, APP_PASSWORD)
    server.sendmail(SENDER_EMAIL, RECIPIENT, msg.as_string())

print("Email sent successfully!")
