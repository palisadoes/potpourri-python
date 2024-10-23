#!/usr/bin/env python3
"""Creates a file containing a list of Thunderbird CLI email commands."""

# Standard imports
import argparse
import os
import sys


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
from rain.Y2024.mailer import Person, MailAuth, Mail
from rain.Y2024.mailer import email as lib_email
from rain.Y2024 import log
from rain import misc
from rain.Y2024.mailer import humans


def main():
    """Main Function."""
    # Get the CLI arguments
    args = cli()
    human_file = os.path.abspath(os.path.expanduser(args.human_file))

    # Log start
    log_message = 'Starting analysis job'
    log.log2debug(9000, log_message)

    # Get human records
    humans_ = humans.Humans(human_file)

    # Process
    everyone = humans_.complete()
    lookup = humans.histogram(everyone, individuals_only=not args.teams)

    # Print result
    for key, value in sorted(lookup.items(), key=lambda item: item[1]):
        print(key, '\t', value)

    # Log stop
    log_message = 'Analysis job complete'
    log.log2debug(9001, log_message)


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
        '--human_file', type=str, required=True,
        help='Scraper TSV file containing contacts.')
    parser.add_argument(
        '--teams',
        help='Process both teams and individuals when specifying states.',
        action='store_true')

    # Parse and return
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()
