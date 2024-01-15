"""Application logging module."""

from __future__ import print_function
import os
import time
import datetime

import yaml


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
