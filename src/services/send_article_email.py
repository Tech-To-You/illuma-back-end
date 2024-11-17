import os

from dotenv import load_dotenv

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from services.generate_articles_as_html import generate_articles_as_html


load_dotenv()

mail_sender = os.getenv("MAIL_SENDER")
mail_sender_password = os.getenv("MAIL_SENDER_PASSWORD")

def send_article_email(receiver_email, articles):
  try:
    email_html = generate_articles_as_html(articles)

    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    email_content = MIMEMultipart()
    email_content["From"] = mail_sender
    email_content["To"] = receiver_email
    email_content["Subject"] = "Recomendações de artigos | Illuma"
    email_content.attach(MIMEText(email_html, "html"))


    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(mail_sender, mail_sender_password)


    server.sendmail(mail_sender, receiver_email, email_content.as_string())
    server.quit()

    return { "status": 200, "message": f"Email enviado com sucesso para {receiver_email}" }
  except Exception as e:
    print("ERROR", e)
    return { "status": 500, "mesage": "Não foi possível enviar o email de recomendação de artigos!" }