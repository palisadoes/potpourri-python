#!/usr/bin/env python3
"""Create Thunderbird email from the CLI."""

# Standard imports
import argparse
import subprocess
import shlex
import os
import sys
from email.headerregistry import Address

# PIP imports
import yaml

# Try to create a working PYTHONPATH
_BIN_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
_ROOT_DIRECTORY = os.path.abspath(os.path.join(_BIN_DIRECTORY, os.pardir))
_EXPECTED = '{0}potpourri-python{0}bin'.format(os.sep)
if _BIN_DIRECTORY.endswith(_EXPECTED) is True:
    sys.path.append(_ROOT_DIRECTORY)
else:
    print('''This script is not installed in the "{0}" directory. Please fix.\
'''.format(_EXPECTED))
    sys.exit(2)

# Library imports
from mailer import Person, MailAuth, Mail
from mailer import email as lib_email


def main():
    """Main Function."""
    # Get the CLI arguments
    args = cli()

    # Get configuration
    config_filepath = os.path.abspath(os.path.expanduser(args.config))
    with open(config_filepath) as fh_:
        config = yaml.safe_load(fh_)

    # Get email account information
    sender = Address(
        display_name='{} {}'.format(config['firstname'], config['lastname']),
        username=config['username'].split('@')[0],
        domain=config['username'].split('@')[1]
    )
    recipient = sender

    # Read the email body
    textfile = os.path.abspath(os.path.expanduser(config['textfile']))
    with open(textfile) as fh_:
        body = fh_.read()

    # Read the email attachment
    imagefile = os.path.abspath(os.path.expanduser(config['imagefile']))

    # Get authentication information
    auth_ = MailAuth(username=config['username'], password=config['password'])
    mail_ = Mail(
        sender=sender,
        receiver=recipient,
        body=body,
        subject=args.subject,
        attachments=[imagefile]
    )

    # Send the email
    lib_email.send(auth_, mail_)


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

    # Parse and return
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()
