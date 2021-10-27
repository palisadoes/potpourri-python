#!/usr/bin/env python3
"""Sends email using Thunderbird."""

# Standard imports
import argparse
import os
import sys
import subprocess
import shlex

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
from rain.mailer import email as lib_email
from rain import log


def main():
    """Main Function."""
    # Initialize key variables
    count = 0
    interval = 5

    # Get the CLI arguments
    args = cli()
    _campaign = lib_email.campaign_files(
        args.campaign, cache_directory=args.cache_directory)
    input_file = _campaign.thunderbird_file

    # Log start
    log_message = 'Starting Thunderbird sending job'
    log.log2debug(5000, log_message)

    # Read body_file into a string
    with open(input_file, 'r') as fh_:
        lines = fh_.readlines()
    records = [_.strip() for _ in lines if '#' not in _]

    for record in records:
        count += 1
        print(count)

        # Process command
        with subprocess.Popen(
            shlex.split(record),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE) as process:
            stdoutdata, stderrdata = process.communicate()
            returncode = process.returncode

        if count % interval == 0:
            input('Press any key to continue...')

    # Log stop
    log_message = 'Thunderbird sending job complete'
    log.log2debug(5001, log_message)


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
        '--campaign', type=str, required=True,
        help='''\
Name of the email campaign. This is used to determine the name of the \
Thunderbird file to ingest.'''
        )
    parser.add_argument(
        '--cache_directory', type=str,
        help='Cache directory where campaign files are stored.')

    # Parse and return
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()
