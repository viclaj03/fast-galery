import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import configparser

def send_recovery_email(to_email: str, recovery_code: str):
    # Leemos el .ini y Configuramos el servidor SMTP
    config = configparser.ConfigParser()
    config.read("config.ini")
    smtp_server = config.get("Email", "smtp_server")
    smtp_port = config.getint("Email", "smtp_port")
    smtp_username = config.get("Email", "smtp_username")
    smtp_password = config.get("Email", "smtp_password")

    # Creamos el mensaje de correo electrónico
    
    subject = "Recuperación de Contraseña"
    body = f"Tu código de recuperación es: {recovery_code} \n <h1>Tiene 10 minutos para cambiar su contraseña</h1>"
    sender_email = smtp_username
    receiver_email = to_email

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))

    # Establece la conexión y envía el correo electrónico
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            
            server.login(smtp_username,smtp_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Correo electrónico enviado con éxito.") 
    except Exception as e: 
        print(f"Error al enviar el correo electrónico: {str(e)}")  