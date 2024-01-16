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
from collections import namedtuple

# Application imports
from rain.Y2024 import log
from rain.Y2024.mailer import html


class Thunderbird:
    """Class to generate Thunderbird records."""

    def __init__(
        self,
        campaign,
        body_file,
        subject,
        sender,
        attachment=None,
    ):
        """Initialize the class.

        Args:
            campaign: Campaign object
            body_file: Text file of content to send
            subject: Subject of email
            sender: Sender
            attachment: Name of file to attach to the email

        Returns:
            None

        """
        # Initialize key variables
        self._campaign = campaign
        self._subject = subject
        self._sender = sender
        self._attachment = attachment

        # Read body_file into a string
        with open(body_file, "r", encoding="utf-8") as fh_:
            self._body = fh_.read()

    def generate(self, persons, label=None, spanish=False):
        """Create a thunderbird command file to send emails.

        Args:
            persons: List of person objects
            label: Label separator to use between batches of persons
            spanish: True if spanish greeting is required

        Returns:
            None
        """
        # Initialize key variables
        uniques = {}

        # Create a unique list of persons
        for person in persons:
            uniques[person.email] = person
        targets = list(uniques.values())

        # Update files
        self.append(targets, label=label, spanish=spanish)

    def append(self, persons, label=None, spanish=False):
        """Create a thunderbird command file to send emails.

        Args:
            persons: List of person objects
            label: Label separator to use between batches of persons
            spanish: True if spanish greeting is required


        Returns:
            None

        """
        # Initialize key variables
        emails = []
        valids = []
        lines = []

        # Define the attachment to use
        if bool(self._attachment) is True:
            attachment = f",attachment='{self._attachment}'"
        else:
            attachment = ""

        # Get emails previously sent
        if os.path.isfile(self._campaign.history_file) is True:
            with open(
                self._campaign.history_file, "r", encoding="utf-8"
            ) as fh_:
                emails = [_.strip() for _ in fh_.readlines()]

        # Filter emails
        for person in persons:
            # Don't prepare to send email to obvious support address
            if _support(person) is True:
                continue

            if person.email not in emails:
                valids.append(person)

        # Create mailto links
        for person in valids:
            # Create first and last names
            if not bool(person.individual):
                recipient = _recipient()
                f_name = recipient.firstname
                l_name = recipient.lastname
                greeting = "Hello" if not bool(spanish) else "Estimado Equipo"
            else:
                f_name = person.firstname
                l_name = person.lastname
                greeting = (
                    person.firstname
                    if not bool(spanish)
                    else f"Estimado {person.firstname}"
                )

            # Create a temporary file with the email body
            with tempfile.NamedTemporaryFile(
                mode="w",
                delete=False,
                suffix=".html",
                dir=self._campaign.cache_directory,
            ) as fh_:
                fh_.write(f"{self._body.replace('XXXXXXXXXX', greeting)}")
                filepath = pathlib.Path(fh_.name)

            # Create entry for output file
            command = f"""\
/usr/bin/thunderbird -compose "\
to='\\"{f_name} {l_name}\\"<{person.email}>',\
from='{self._sender}',\
subject='{self._subject}',\
message='{filepath}'\
{attachment}"\
"""
            lines.append(command)

        # Write to output file
        with open(
            self._campaign.thunderbird_file, "a", encoding="utf-8"
        ) as fh_:

            # Write the Thunderbird command entries
            if bool(label):
                fh_.write(f"# {label.upper()}\n")

            # Write the Thunderbird command entries
            for line in lines:
                fh_.write(f"{line}\n")

        # Write to history file
        with open(self._campaign.history_file, "a", encoding="utf-8") as fh_:
            for person in valids:
                fh_.write(f"{person.email}\n")


class Mailto:
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
            with open(self._history, "r", encoding="utf-8") as fh_:
                emails = [_.strip() for _ in fh_.readlines()]

        # Filter emails
        for person in persons:
            if person.email not in emails:
                valids.append(person)

        # Create mailto links
        for person in valids:
            # Create first and last names
            if not bool(person.individual):
                recipient = _recipient()
                f_name = recipient.firstname
                l_name = recipient.lastname
                greeting = "Hello"
            else:
                f_name = person.firstname
                l_name = person.lastname
                greeting = person.firstname

            # Create links
            links.append(
                f"""\
<a href="mailto:&quot;{f_name}%20{l_name}&quot;&lt;{person.email}&gt;?\
subject={'%20'.join(self._subject.split())}&body={greeting}%2C%0A">\
{person.organization}</a><br>\
"""
            )

        # Write to output file
        with open(self._output, "a", encoding="utf-8") as fh_:
            for link in links:
                fh_.write(f"{link}\n")

        # Write to history file
        with open(self._history, "a", encoding="utf-8") as fh_:
            for person in valids:
                fh_.write(f"{person.email}\n")


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
    firstname = (
        mail.receiver.firstname if bool(mail.receiver.firstname) else "Hello"
    )

    # Create SMTP TLS session
    client = smtplib.SMTP("smtp.gmail.com", 587)
    try:
        client.ehlo()
    except:
        _exception = sys.exc_info()
        log_message = "Gmail Communication Failure"
        log.log2exception(1013, _exception, message=log_message)
    client.starttls()

    # Authentication
    try:
        client.login(auth.username, auth.password)
    except:
        _exception = sys.exc_info()
        log_message = "Gmail Authentication Failure"
        log.log2exception(1014, _exception, message=log_message)
        return success

    # Format message
    message = MIMEMultipart()
    message["Subject"] = mail.subject
    message["From"] = _address(mail.sender)
    message["To"] = _address(mail.receiver)

    # Format body
    html_ = f"""
<html>
    <head></head>
    <body>
        <font face="arial">
        <p>{firstname},</p>
            {html.File(mail.body).body()}
        <br/><img src="cid:{content_id}"/>
        </font>
    </body>
</html>
"""

    message.attach(MIMEText(html_, "html", "UTF-8"))

    # Add attachment if required
    if bool(mail.image) is True:
        with open(mail.image, "rb") as fh_:
            part = MIMEImage(fh_.read())
            part.add_header("Content-ID", f"<{content_id}>")
        message.attach(part)

    # Send
    try:
        client.sendmail(
            mail.sender.email, mail.receiver.email, message.as_string()
        )
        success = True
    except:
        _exception = sys.exc_info()
        log_message = "Gmail Send Failure"
        log.log2exception(1015, _exception, message=log_message)
        return success
    finally:
        client.quit()
    return success


def _support(person):
    """Determine whether person could generate a support ticket.

    Args:
        person: Person object

    Returns:
        result: Support contact if True

    """
    # Initialize key variables
    result = False
    prefixes = ["support", "help", "abuse"]
    for prefix in prefixes:
        if prefix.lower() in person.firstname.lower():
            result = True
        if prefix.lower() in person.lastname.lower():
            result = True
        if prefix.lower() in person.email.lower():
            result = True

    # Return
    return result


def _address(person):
    """Create address object.

    Args:
        person: Person object

    Returns:
        result: Address object

    """
    # Initialize key variables
    f_name = person.firstname if bool(person.firstname) else "Technical"
    l_name = person.lastname if bool(person.lastname) else "Team"

    # Return
    result = formataddr((f"{f_name} {l_name}", person.email))
    return result


def _recipient():
    """Strip non alphanumeric characters.

    Args:
        None

    Returns:
        result: alphanumeric string

    """
    # Initialize key variables
    Recipient = namedtuple("Recipient", "firstname lastname")
    result = Recipient(firstname="Technical", lastname="Team")
    return result
