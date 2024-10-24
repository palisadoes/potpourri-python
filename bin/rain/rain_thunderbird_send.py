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
from rain.Y2024 import log
from rain.Y2024 import config as _config


def main():
    """Main Function."""
    # Initialize key variables
    count = 0
    interval = 5
    response = ''

    # Get the CLI arguments
    args = cli()

    # Create a config object
    config = _config.Config(args.config_file)

    # Create a campaign object
    campaign = _config.campaign(config, args.campaign_name)

    # Log start
    log_message = "Starting Thunderbird sending job"
    log.log2debug(5000, log_message)

    # Read body_file into a string
    with open(campaign.thunderbird_file, "r", encoding="utf-8") as fh_:
        lines = fh_.readlines()
    records = [_.strip() for _ in lines if "#" not in _]

    for record in records:
        count += 1
        print(count)

        # Process command
        with subprocess.Popen(
            shlex.split(record), stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as process:
            _, __ = process.communicate()
            _ = process.returncode

        if count % interval == 0:
            response = input("Press any key to continue...")
        
            # Test result
            if bool(response.strip()) is True:
                break

    # Log stop
    log_message = "Thunderbird sending job complete"
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
        "--campaign_name",
        type=str,
        required=True,
        help="""\
Name of the email campaign. This is used to determine the name of the \
Thunderbird file to ingest.""",
    )
    parser.add_argument(
        "--config_file",
        type=str,
        help="Name of the configuration file.",
    )

    # Parse and return
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
