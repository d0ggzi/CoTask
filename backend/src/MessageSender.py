import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

subject = "Deadline changes in cotask"
sender = "ashinyakov@bk.ru"
password = 'WsM8SJGqasqn39x4CLjz'


def send_message(mes: str, email: str):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = email

        msg.attach(MIMEText(mes, 'plain'))

        server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
        server.login(sender, password)
        text = msg.as_string()
        server.sendmail(sender, email, text)
        server.quit()
    except Exception as e:
        print(f"Error occured while sending to {email}")
