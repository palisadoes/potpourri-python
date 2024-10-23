#!/usr/bin/env python3
"""Mailing script."""

# Standard imports
import argparse
import os
import sys

# PIP imports
import yaml

# Try to create a working PYTHONPATH
_BIN_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
_ROOT_DIRECTORY = os.path.abspath(
    os.path.join(
        os.path.abspath(os.path.join(_BIN_DIRECTORY, os.pardir)), os.pardir
    )
)
_EXPECTED = f"{os.sep}potpourri-python{os.sep}bin{os.sep}rain"
if _BIN_DIRECTORY.endswith(_EXPECTED) is True:
    sys.path.append(_ROOT_DIRECTORY)
else:
    print(
        f"""\
This script is not installed in the "{_EXPECTED}" directory. Please fix.\
"""
    )
    sys.exit(2)

# Library imports
from rain.mailer import Person, MailAuth, Mail
from rain.mailer import email as lib_email
from rain import log
from rain.mailer import humans


def main():
    """Main Function."""
    # Get the CLI arguments
    args = cli()

    # Log start
    log_message = 'Starting mailer job'
    log.log2debug(1000, log_message)

    # Get configuration
    config_filepath = os.path.abspath(os.path.expanduser(args.config))
    with open(config_filepath) as fh_:
        config = yaml.safe_load(fh_)

    # Get email account information
    sender = Person(
        firstname=config['firstname'],
        lastname=config['lastname'],
        email=config['username'],
        individual=True,
        validated=True
    )

    # Get humans
    persons = humans.Humans(
        os.path.abspath(os.path.expanduser(args.human_file)))
    recipients = persons.uniques()

    sys.exit(0)

    # See output
    print(recipients)
    sys.exit(0)

    # Read the email body
    textfile = os.path.abspath(os.path.expanduser(args.html_file))
    with open(textfile) as fh_:
        body = fh_.read()

    # Read the email attachment
    imagefile = os.path.abspath(os.path.expanduser(args.image_file))

    # Get authentication information
    auth_ = MailAuth(username=config['username'], password=config['password'])

    # Send mail to each recipient
    for recipient in recipients:
        mail_ = Mail(
            sender=sender,
            receiver=recipient,
            body=body,
            subject=args.subject,
            image=imagefile
        )

        # Send the email
        result = lib_email.send(auth_, mail_)
        if bool(result) is True:
            log_message = 'Successfully sent to {}'.format(recipient.email)
            log.log2debug(1002, log_message)
        else:
            log_message = 'Failed to send to {}'.format(recipient.email)
            log.log2debug(1002, log_message)

    # Log stop
    log_message = 'Mailer job complete'
    log.log2debug(1001, log_message)


def cli():
    """Parse the CLI.

    Args:
        args: None

    Returns:
        args: ArgumentParser

    """
    # Initialize key variables
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config', type=str, required=True)
    parser.add_argument(
        '--subject', type=str, required=True)
    parser.add_argument(
        '--image_file', type=str, required=True)
    parser.add_argument(
        '--html_file', type=str, required=True)
    parser.add_argument(
        '--human_file', type=str, required=True)

    # Parse and return
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()
