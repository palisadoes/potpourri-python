"""Application module to manage email communication."""

# Standard imports
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

# Application imports
from mailer import log


def send(auth, mail):
    """Read a configuration file.

    Args:
        auth: Namedtuple with Authentication parameters
        mail: Namedtuple with mail contents

    Returns:
        success: True if succesful

    """
    # Initialize key variables
    success = False

    # Create SMTP TLS session
    client = smtplib.SMTP('smtp.gmail.com', 587)
    try:
        client.ehlo()
    except:
        _exception = sys.exc_info()
        log_message = 'Gmail Communication Failure'
        log.log2exception(1013, _exception, message=log_message)
    client.starttls()

    # Authentication
    try:
        client.login(auth.username, auth.password)
    except:
        _exception = sys.exc_info()
        log_message = 'Gmail Authentication Failure'
        log.log2exception(1014, _exception, message=log_message)
        return success

    # Format message
    message = MIMEMultipart()
    message['Subject'] = mail.subject
    message['From'] = mail.sender
    message['To'] = mail.receiver
    # print(mail.sender)
    # message.add_header('reply-to', mail.sender)
    # message.add_header('reply-to', mail.sender)
    html = '''
<html>
    <head></head>
    <body><font face="courier">
        {}
    </font></body>
</html>
'''.format('<br>'.join('&nbsp;'.join(mail.body.split(' ')).split('\n')))

    message.attach(MIMEText(html, 'html', 'UTF-8'))

    # Add attachment if required
    if bool(mail.attachments) is True:
        if isinstance(mail.attachments, list) is True:
            for attachment in mail.attachments:
                part = MIMEApplication(open(attachment, 'rb').read())
                part.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=('{}'.format(attachment)))
                message.attach(part)

    # Send
    try:
        client.sendmail(
            mail.sender, mail.receiver, message.as_string())
        success = True
    except:
        _exception = sys.exc_info()
        log_message = 'Gmail Send Failure'
        log.log2exception(1015, _exception, message=log_message)
        return success
    finally:
        client.quit()
    return success
