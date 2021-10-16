"""Application module to manage email communication."""

# Standard imports
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import uuid

# Application imports
from rain import log
from rain.mailer import html


def send(auth, mail):
    """Send mail.

    Args:
        auth: Namedtuple with Authentication parameters
        mail: Namedtuple with mail contents

    Returns:
        success: True if succesful

    """
    # Initialize key variables
    success = False
    content_id = str(uuid.uuid4())
    firstname = mail.receiver.firstname if bool(
        mail.receiver.firstname) else 'Hello'

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
    message['From'] = _address(mail.sender)
    message['To'] = _address(mail.receiver)

    # Format body
    html_ = '''
<html>
    <head></head>
    <body>
        <font face="arial">
        <p>{},</p>
            {}
        <br/><img src="cid:{}"/>
        </font>
    </body>
</html>
'''.format(firstname, html.File(mail.body).body(), content_id)

    message.attach(MIMEText(html_, 'html', 'UTF-8'))

    # Add attachment if required
    if bool(mail.image) is True:
        with open(mail.image, 'rb') as fh_:
            part = MIMEImage(fh_.read())
            part.add_header('Content-ID', '<{}>'.format(content_id))
        message.attach(part)

    # Send
    try:
        client.sendmail(
            mail.sender.email, mail.receiver.email, message.as_string())
        success = True
    except:
        _exception = sys.exc_info()
        log_message = 'Gmail Send Failure'
        log.log2exception(1015, _exception, message=log_message)
        return success
    finally:
        client.quit()
    return success


def _address(person):
    """Create address object.

    Args:
        person: Person object

    Returns:
        result: Address object

    """
    # Initialize key variables
    f_name = person.firstname if bool(person.firstname) else 'Arin'
    l_name = person.lastname if bool(person.lastname) else 'Contact'

    # Return
    result = formataddr(('{} {}'.format(f_name, l_name), person.email))
    return result
