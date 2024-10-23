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
from rain.Y2024.mailer import email as lib_email
from rain.Y2024 import log
from rain.Y2024 import misc
from rain.Y2024.mailer import humans
from rain.Y2024 import config as _config


def main():
    """Main Function."""
    # Initialize key variables
    timestamp = None

    # Get the CLI arguments
    args = cli()
    human_file = os.path.abspath(os.path.expanduser(args.human_file))
    body_file = os.path.abspath(os.path.expanduser(args.body_file))

    # Get timestamp
    if bool(args.date) is True:
        timestamp = misc.timestamp(args.date)

    # Create a config object
    config = _config.Config(args.config_file)

    # Create a campaign object
    campaign = _config.campaign(config, args.campaign_name)

    # Log start
    log_message = "Starting Thunderbird file creation job"
    log.log2debug(4000, log_message)

    # Get human records
    humans_ = humans.Humans(human_file)
    everyone = humans_.complete()

    # Filter persons
    strainer_ = humans.Strainer(everyone)

    # Create object for generating emails
    thunderbird = lib_email.Thunderbird(
        campaign,
        body_file,
        args.subject,
        args.sender,
    )

    # process Anglophone organizations
    if not args.spanish:
        # Process GOATs
        people = humans.goats(humans_)
        thunderbird.generate(people, label="Goats")

        # Process Caribbean
        people = strainer_.caribbean()
        thunderbird.generate(people, label="Caribbean")

        # Process Educational
        people = strainer_.edu(individuals_only=True)
        thunderbird.generate(people, label="Educational")

        # Process states/provinces with few organizations
        people = strainer_.smallfry(individuals_only=True, strict=True)
        thunderbird.generate(people, label="SmallFry")

    # Process state
    if bool(args.states) is True:
        for state in args.states.split(","):
            # Update the stuff
            people = strainer_.state(
                state.upper(),
                individuals_only=not bool(args.teams),
                timestamp=timestamp,
                strict=True,
            )
            thunderbird.generate(
                people, label=state.upper(), spanish=args.spanish
            )

    # Log stop
    log_message = "Thunderbird file creation job complete"
    log.log2debug(4001, log_message)


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
        "--subject",
        type=str,
        required=True,
        help="Subject of email to be sent.",
    )
    parser.add_argument(
        "--sender",
        type=str,
        required=True,
        help="""\
Thunderbird sender in format "Firstname Lastname <email@example.com>". When \
the Thunderbird client has more than one account, this information is used \
to determine the account to use when sending.""",
    )
    parser.add_argument(
        "--human_file",
        type=str,
        required=True,
        help="Scraper TSV file containing contacts.",
    )
    parser.add_argument(
        "--body_file",
        type=str,
        required=True,
        help="""\
HTML file containing the message to be sent. This file contain the string \
"XXXXXXXXXX" to allow the easy search and replace of the contact name.""",
    )
    parser.add_argument(
        "--campaign_name",
        type=str,
        required=True,
        help="""\
Name of the email campaign. This is used to create a history file to help \
prevent duplicate Thunderbird command entries when repeatedly running \
this script. It is also used to generate the Thunderbird output file name.""",
    )
    parser.add_argument(
        "--states",
        type=str,
        help="""\
Names of states to include when generating Thunderbird email lists""",
    )
    parser.add_argument(
        "--date",
        type=str,
        help="Filter records last updated after this YYYY-MM-DD date.",
    )
    parser.add_argument(
        "--spanish", help="Use Spanish greeting if used.", action="store_true"
    )
    parser.add_argument(
        "--teams",
        help="Process both teams and individuals when specifying states.",
        action="store_true",
    )
    parser.add_argument(
        "--config_file",
        type=str,
        required=True,
        help="Name of the configuration file.",
    )

    # Parse and return
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
