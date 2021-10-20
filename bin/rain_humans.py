#!/usr/bin/env python3
"""Estimate votes per Organization."""

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
    data = {}

    # Get the CLI arguments
    args = cli()

    # Log start
    log_message = 'Starting vote estimae job'
    log.log2debug(3000, log_message)

    # Get human records
    humans_ = humans.Humans(
        os.path.abspath(os.path.expanduser(args.human_file)))
    records = humans_.complete()

    strainer = humans.Strainer(records)
    records = strainer.state('PR')
    # records = strainer.caribbean()
    # records = strainer.country('Canada')
    #
    for record in records:
        print(record)
    return

    # Start counting
    for record in records:
        email = record.email
        if data.get(email):
            data[email] += 1
        else:
            data[email] = 1
        # print('-> {}, {}, {}, {}, {}'.format(record.firstname, record.lastname, record.email, record.state, record.country))

    '''
    Saint Barthelemy
    Guadeloupe
    Martinique
    Saint Martin

    PUERTO RICO
    Virgin Islands, U.S.
    '''

    # Print result
    for email, count in sorted(data.items(), key=lambda item: item[1]):
        # print(email)
        if count > 1:
            print('{:<50}: {}'.format(email, count))

    # Log stop
    log_message = 'Vote estimate job complete'
    log.log2debug(3001, log_message)


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
        '--human_file', type=str, required=True)

    # Parse and return
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()
