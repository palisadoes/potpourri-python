"""Application logging module."""

from __future__ import print_function
import os
import time
import datetime
import re

import yaml

# Application library imports
from rain.Y2024.mailer import Campaign


class Config:
    """Class to manage RAIN configuration."""

    def __init__(self, config_file):
        # Get configuration
        config_filepath = os.path.abspath(os.path.expanduser(config_file))
        with open(config_filepath, encoding="utf-8") as fh_:
            self._config = yaml.safe_load(fh_)

        self._smtp = self._config.get("smtp")
        self._scraper = self._config.get("scraper")
        self._year = datetime.datetime.fromtimestamp(time.time()).strftime(
            "%Y"
        )

    def smtp_firstname(self):
        """Return firstname.

        Args:
            None

        Returns:
            value: Value

        """
        # Return
        value = self._smtp.get("firstname")
        return value

    def smtp_lastname(self):
        """Return lastname.

        Args:
            None

        Returns:
            value: Value

        """
        # Return
        value = self._smtp.get("lastname")
        return value

    def smtp_username(self):
        """Return username.

        Args:
            None

        Returns:
            value: Value

        """
        # Return
        value = self._smtp.get("username")
        return value

    def smtp_password(self):
        """Return password.

        Args:
            None

        Returns:
            value: Value

        """
        # Return
        value = self._smtp.get("password")
        return value

    def smtp_textfile(self):
        """Return textfile.

        Args:
            None

        Returns:
            value: Value

        """
        # Return
        value = self._smtp.get("textfile")
        return value

    def smtp_imagefile(self):
        """Return imagefile.

        Args:
            None

        Returns:
            value: Value

        """
        # Return
        value = self._smtp.get("imagefile")
        return value

    def data_directory(self):
        """Return data_directory.

        Args:
            None

        Returns:
            value: Value

        """
        # Return
        value = self._config.get("data_directory")
        os.makedirs(value, exist_ok=True)
        return value

    def campaign_directory(self):
        """Return campaign_directory.

        Args:
            None

        Returns:
            value: Value

        """
        # Return
        value = f"""\
{self._config.get("data_directory")}{os.sep}campaigns{os.sep}{self._year}"""
        os.makedirs(value, exist_ok=True)
        return value

    def templates_directory(self):
        """Return templates_directory.

        Args:
            None

        Returns:
            value: Value

        """
        # Return
        value = f"""\
{self._config.get("data_directory")}{os.sep}templates{os.sep}{self._year}"""
        os.makedirs(value, exist_ok=True)
        return value

    def scraper_directory(self):
        """Return scraper_directory.

        Args:
            None

        Returns:
            value: Value

        """
        # Return
        value = f"""\
{self._config.get("data_directory")}{os.sep}scraper{os.sep}{self._year}"""
        os.makedirs(value, exist_ok=True)
        return value

    def scraper_output_file(self):
        """Return scraper_output_file.

        Args:
            None

        Returns:
            value: Value

        """
        # Return
        timestamp_part = datetime.datetime.fromtimestamp(time.time()).strftime(
            "%Y%m%d-%H%M%S"
        )
        filename = f"{timestamp_part}.scraper.output.tsv"
        value = f"{self.scraper_directory()}{os.sep}{filename}"
        return value

    def scraper_query_url(self):
        """Return scraper_query_url.

        Args:
            None

        Returns:
            value: Value

        """
        # Return

        value = f'{self._scraper.get("query_url")}'
        return value

    def scraper_entity_url(self):
        """Return scraper_entity_url.

        Args:
            None

        Returns:
            value: Value

        """
        # Return

        value = f'{self._scraper.get("entity_url")}'
        return value


def campaign(config, proposed_name):
    """Create the names of files used to track the email campaign.

    Args:
        config: Config object
        proposed_name: Proposed campaign name

    Returns:
        result: Campaign object

    """
    # Initialize key variables
    regex = re.compile("[^A-Za-z0-9 ]+")

    # Create standardized campaign name
    final_name = "".join(
        [_.title() for _ in regex.sub(" ", proposed_name).split()]
    )

    # Define the campaign's home directory
    this_campaign_directory = (
        f"{config.campaign_directory()}{os.sep}{final_name}"
    )
    os.makedirs(this_campaign_directory, exist_ok=True)

    # Define the campaign's cache directory
    cache_directory = f"{this_campaign_directory}{os.sep}cache"
    os.makedirs(cache_directory, exist_ok=True)

    # Return
    file_path_prefix = f"{this_campaign_directory}{os.sep}"
    result = Campaign(
        history_file=f"{file_path_prefix}campaign-email-addresses.db.txt",
        thunderbird_file=f"{file_path_prefix}thunderbird.entries.txt",
        cache_directory=cache_directory,
        campaign=final_name,
    )
    return result
