"""Application module to manage email communication."""

# Standard imports
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import os
import uuid
import tempfile
import pathlib

# Application imports
from rain import log
from rain.mailer import html


class Thunderbird():
    """Class to generate Thunderbird records."""

    def __init__(self, history_file, output_file, body_file, subject, sender):
        """Initialize the class.

        Args:
            history_file: Contains list of emails previously sent
            output_file: File containing Thunderbird commands
            body_file: Text file of content to send
            subject: Subject of email
            sender: Sender

        Returns:
            None

        """
        # Initialize key variables
        self._history = history_file
        self._output = output_file
        self._subject = subject
        self._sender = sender

        # Read body_file into a string
        with open(body_file, 'r') as fh_:
            self._body = fh_.read()

    def append(self, persons):
        """Send mail.

        Args:
            persons: List of person objects


        Returns:
            None

        """
        # Initialize key variables
        emails = []
        valids = []
        lines = []

        # Get emails previously sent
        if os.path.isfile(self._history) is True:
            with open(self._history, 'r') as fh_:
                emails = [_.strip() for _ in fh_.readlines()]

        # Filter emails
        for person in persons:
            if person.email not in emails:
                valids.append(person)

        # Create mailto links
        for person in valids:
            # Create first and last names
            if not bool(person.individual):
                f_name = 'Technical'
                l_name = 'Contact - {}'.format(
                    person.organization.split()[0].title())
                greeting = 'Hello'
            else:
                f_name = person.firstname
                l_name = person.lastname
                greeting = person.firstname

            # Create a temporary file with the email body
            with tempfile.NamedTemporaryFile(
                    mode='w',
                    delete=False,
                    suffix='.txt',
                    dir=os.path.abspath(
                        os.path.expanduser('~/tmp/thunderbird'))) as fh_:
                fh_.write('{},\n\n{}'.format(greeting, self._body))
                filepath = pathlib.Path(fh_.name)

            # Create entry for output file
            command = '''\
/usr/bin/thunderbird -compose "\
to='{0} {1} <{2}>',\
from='{3}',\
subject='{4}',\
message='{5}'\
"\
'''.format(
    f_name, l_name, person.email, self._sender, self._subject, filepath)
            lines.append(command)

        # Write to output file
        with open(self._output, 'a') as fh_:
            for line in lines:
                fh_.write('{}\n'.format(line))

        # Write to history file
        with open(self._history, 'a') as fh_:
            for person in valids:
                fh_.write('{}\n'.format(person.email))


class Mailto():
    """Class to generate mailto records."""

    def __init__(self, history_file, output_file, subject):
        """Initialize the class.

        Args:
            history_file: Contains list of emails previously sent
            output_file: File containing mailto links
            subject: Subject of email

        Returns:
            None

        """
        # Initialize key variables
        self._history = history_file
        self._output = output_file
        self._subject = subject

    def append(self, persons):
        """Send mail.

        Args:
            persons: List of person objects


        Returns:
            None

        """
        # Initialize key variables
        emails = []
        valids = []
        links = []

        # Get emails previously sent
        if os.path.isfile(self._history) is True:
            with open(self._history, 'r') as fh_:
                emails = [_.strip() for _ in fh_.readlines()]

        # Filter emails
        for person in persons:
            if person.email not in emails:
                valids.append(person)

        # Create mailto links
        for person in valids:
            # Create first and last names
            if not bool(person.individual):
                f_name = 'Technical'
                l_name = 'Contact - {}'.format(
                    person.organization.split()[0].title())
                greeting = 'Hello'
            else:
                f_name = person.firstname
                l_name = person.lastname
                greeting = person.firstname

            # Create links
            links.append('''\
<a href="mailto:&quot;{}%20{}&quot;&lt;{}&gt;?\
subject={}&body={}%2C%0A">{}</a><br>\
'''.format(f_name, l_name, person.email,'%20'.join(self._subject.split()),
           greeting, person.organization))

        # Write to output file
        with open(self._output, 'a') as fh_:
            for link in links:
                fh_.write('{}\n'.format(link))

        # Write to history file
        with open(self._history, 'a') as fh_:
            for person in valids:
                fh_.write('{}\n'.format(person.email))


def send(auth, mail):
    """Send mail.

    Args:
        auth: Namedtuple with Authentication parameters
        mail: Namedtuple with mail contents

    Returns:
        success: True if succesful

    """
    # Short circuit
    return False

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
    f_name = person.firstname if bool(person.firstname) else 'Ar''in'
    l_name = person.lastname if bool(person.lastname) else 'Contact'

    # Return
    result = formataddr(('{} {}'.format(f_name, l_name), person.email))
    return result
