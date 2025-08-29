import smtplib
from email.mime.text import MIMEText
from flask import send_file
import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas

def send_email(to_email, subject, body):
    sender = 'your_email@gmail.com'
    password = 'your_password'
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to_email

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)

def generate_csv(tickets):
    df = pd.DataFrame([{
        'Ticket ID': t.id,
        'Issue Type': t.issue_type,
        'Description': t.description,
        'Status': t.status,
        'Created By': t.created_by,
        'Assigned To': t.assigned_to,
        'Created At': t.created_at
    } for t in tickets])
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return output

def generate_pdf(tickets):
    output = BytesIO()
    c = canvas.Canvas(output)
    y = 800
    for t in tickets:
        c.drawString(50, y, f"Ticket ID: {t.id}, Type: {t.issue_type}, Status: {t.status}")
        y -= 20
    c.save()
    output.seek(0)
    return output
