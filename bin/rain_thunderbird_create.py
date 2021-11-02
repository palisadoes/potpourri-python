#!/usr/bin/env python3
"""Creates a file containing a list of Thunderbird CLI email commands."""

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
from rain import misc
from rain.mailer import humans


def main():
    """Main Function."""
    # Initialize key variables
    timestamp = None

    # Get the CLI arguments
    args = cli()
    human_file = os.path.abspath(os.path.expanduser(args.human_file))
    body_file = os.path.abspath(os.path.expanduser(args.body_file))
    if bool(args.cache_directory):
        cache_directory = os.path.abspath(
            os.path.expanduser(args.cache_directory))

    # Get timestamp
    if bool(args.date) is True:
        timestamp = misc.timestamp(args.date)

    # Determine the output filename
    _campaign = lib_email.campaign_files(
        args.campaign, cache_directory=cache_directory)
    output_file = _campaign.thunderbird_file

    # Log start
    log_message = 'Starting Thunderbird file creation job'
    log.log2debug(4000, log_message)

    # Get human records
    humans_ = humans.Humans(human_file)
    everyone = humans_.complete()

    # Filter persons
    strainer_ = humans.Strainer(everyone)
    caribbean = strainer_.caribbean()

    # Create object for generating emails
    thunderbird = lib_email.Thunderbird(
        args.campaign, body_file, args.subject,
        args.sender, cache_directory=cache_directory)

    # Process GOATs
    label(output_file, 'Goats')
    goats = humans.goats(humans_)
    generator(thunderbird, goats)

    # Process Caribbean
    label(output_file, 'Caribbean')
    generator(thunderbird, caribbean)

    # Process state
    if bool(args.states) is True:
        for state in args.states.split(','):
            # Update the stuff
            label(output_file, state.upper())
            citizens = strainer_.state(
                state.upper(), individuals_only=True,
                timestamp=timestamp, strict=True)
            generator(thunderbird, citizens, spanish=args.spanish)

    # Log stop
    log_message = 'Thunderbird file creation job complete'
    log.log2debug(4001, log_message)


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


def generator(thunderbird, persons, spanish=False):
    """Generate thunderbird entries for Person.

    Args:
        thunderbird: email.Thunderbird object
        persons: List of person objects
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
    thunderbird.append(targets, spanish=spanish)


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
    parser.add_argument(
        '--states', type=str,
        help='''\
Names of states to include when generating Thunderbird email lists''')
    parser.add_argument(
        '--date', type=str,
        help='Filter records last updated after this YYYY-MM-DD date.')
    parser.add_argument(
        '--spanish', help='Use Spanish greeting if used.', action='store_true')

    # Parse and return
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()
