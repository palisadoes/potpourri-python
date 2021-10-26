#!/usr/bin/env python3
"""Creates HTML file with mailto links."""

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
    output_file = os.path.abspath(os.path.expanduser(args.output_file))
    history_file = os.path.abspath(os.path.expanduser(args.history_file))

    # Log start
    log_message = 'Starting Mailto job'
    log.log2debug(3000, log_message)

    # Get human records
    humans_ = humans.Humans(human_file)
    everyone = humans_.complete()

    # Filter persons
    strainer_ = humans.Strainer(everyone)
    caribbean = strainer_.caribbean()

    # Create object for generating emails
    mailto = lib_email.Mailto(history_file, output_file, args.subject)

    # Process GOATs
    label(args.output_file, 'Goats')
    goats = humans.goats(humans_)
    generator(mailto, goats)

    # Process Caribbean
    label(args.output_file, 'Caribbean')
    generator(mailto, caribbean)

    # Process state
    if bool(args.states) is True:
        for state in args.states.split(','):
            # Update the stuff
            label(args.output_file, state.upper())
            citizens = strainer_.state(state.upper(), individuals_only=True)
            generator(mailto, citizens)

    # Log stop
    log_message = 'Mailto estimate job complete'
    log.log2debug(3001, log_message)


def label(filename, label_):
    """Add HTML label to file.

    Args:
        filename: Name of file
        label_: Label to write

    Returns:
        None
    """
    # Write to output file
    with open(filename, 'a') as fh_:
        fh_.write('<br><b>{}</b><br>\n'.format(label_.upper()))


def generator(mailto, persons):
    """Generate mailto entries for Person.

    Args:
        mailto: email.Mailto object
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
    mailto.append(targets)


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
    parser.add_argument(
        '--output_file', type=str, required=True,
        default='~/tmp/rain/Mailto-Output.html')
    parser.add_argument(
        '--history_file', type=str, required=True,
        default='~/tmp/rain/Mailto-History.db')
    parser.add_argument(
        '--subject', type=str, required=True)
    parser.add_argument(
        '--states', type=str)

    # Parse and return
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()
