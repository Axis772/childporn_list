#!/usr/bin/python3
#-----------------------------------------------------------------------------
# Descripcion:
# Fecha Creacion: 26 Sep 2018
# Descripcion:    Envio de correo electronico usando BT Axigen server
#-----------------------------------------------------------------------------

#*****************************************************************************
# Library Load
#*****************************************************************************
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
#******************************************************************************

#******************************************************************************
# Funtions
#******************************************************************************


def enviar(para, subject, message):
    username = "dns-adm@btlatam.com.co"
    password = "dns-adm"
    smtphost = "kraken.btlatam.com.co"
    smtpport = 25
    # Create message object instance
    msg = MIMEMultipart()
    # Declare message elements
    msg['From'] = "dns-adm@btlatam.com.co"
    msg['To'] = para
    msg['Subject'] = subject
    # Step 6 - Add the message body to the object instance
    msg.attach(MIMEText(message, 'plain'))
    # Step 7 - Create the server connection
    server = smtplib.SMTP(smtphost, smtpport)
    # Authenticate with the server
    server.login(username, password)
    # Send the message
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    # Disconnect
    server.quit()

#******************************************************************************
