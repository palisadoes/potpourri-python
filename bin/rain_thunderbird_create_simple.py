#!/usr/bin/env python3
"""Sends email using Thunderbird."""

# Standard imports
import argparse
import os
import sys


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
from rain.mailer import Person, MailAuth, Mail
from rain.mailer import email as lib_email
from rain import log
from rain.mailer import humans


def main():
    """Main Function."""
    # Initialize key variables

    # Get the CLI arguments
    args = cli()
    human_file = os.path.abspath(os.path.expanduser(args.human_file))
    body_file = os.path.abspath(os.path.expanduser(args.body_file))
    cache_directory = os.path.abspath(os.path.expanduser(args.cache_directory))

    # Determine the output filename
    _campaign = lib_email.campaign_files(
        args.campaign, cache_directory=cache_directory)
    output_file = _campaign.thunderbird_file

    # Log start
    log_message = 'Starting Thunderbird file creation job'
    log.log2debug(6000, log_message)

    # Get human records
    humans_ = humans.SimpleHumans(human_file)
    everyone = humans_.complete()

    # Create object for generating emails
    thunderbird = lib_email.Thunderbird(
        args.campaign, body_file, args.subject,
        args.sender, cache_directory=cache_directory)

    # Process Everyone
    label(output_file, 'Everyone Email')
    generator(thunderbird, everyone)

    # Log stop
    log_message = 'Thunderbird file creation job complete'
    log.log2debug(6001, log_message)


def label(filename, label_):
    """Add label comment to file.

    Args:
        filename: Name of file
        label_: Label to write

    Returns:
        None
    """
    # Write to output file
    with open(filename, 'a') as fh_:
        fh_.write('# {}\n'.format(label_.upper()))


def generator(thunderbird, persons):
    """Generate thunderbird entries for Person.

    Args:
        thunderbird: email.Thunderbird object
        persons: List of person objects

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
    thunderbird.append(targets)


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
        '--subject', type=str, required=True,
        help='Subject of email to be sent.')
    parser.add_argument(
        '--sender', type=str, required=True,
        help='''\
Thunderbird sender in format "Firstname Lastname <email@example.com>". When \
the Thunderbird client has more than one account, this information is used \
to determine the account to use when sending.''')
    parser.add_argument(
        '--human_file', type=str, required=True,
        help='Scraper TSV file containing contacts.')
    parser.add_argument(
        '--body_file', type=str, required=True,
        help='''\
HTML file containing the message to be sent. This file contain the string \
"XXXXXXXXXX" to allow the easy search and replace of the contact name.''')
    parser.add_argument(
        '--campaign', type=str, required=True,
        help='''\
Name of the email campaign. This is used to create a history file to help \
prevent duplicate Thunderbird command entries when repeatedly running \
this script. It is also used to generate the Thunderbird output file name.''')
    parser.add_argument(
        '--cache_directory', type=str,
        help='Cache directory where campaign files are stored.')

    # Parse and return
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()
