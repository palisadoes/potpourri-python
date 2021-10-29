#!/usr/bin/env python3
"""Scraper."""

# Standard imports
import argparse
import os
import sys
import re
import json
import urllib.request
from collections import namedtuple
import time
import random
import csv

# PIP imports

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
from rain import log


class Org():
    """Extract data from Organization."""

    def __init__(self, data):
        """Initialize the class.

        Args:
            data: JSON data

        Returns:
            None

        """
        # Initialize key variables
        self._data = data

    def business(self):
        """Get business data.

        Args:
            None

        Returns:
            result: Business object

        """
        # Initialize key variables
        Business = namedtuple(
            'Business', 'handle org address kind registration updated')
        result = None
        registration = None

        # Get org data
        handle = self._data.get('handle')

        # Get the registration date
        events = self._data.get('events')
        if bool(events) is True:
            for event in events:
                if event.get('eventAction') == 'registration':
                    registration = event.get('eventDate')

        # Get data from vcard
        vcard = self._data['vcardArray'][1]
        for item in vcard:
            if bool(item) is True:
                if item[0] == 'fn':
                    org = item[-1]
                if item[0] == 'adr':
                    address = '\n'.join(item[1]['label'].split('\r'))
                    address = ':'.join(address.split('\n'))
                if item[0] == 'kind':
                    kind = item[-1]

        # Get name and email
        result = Business(
            handle=handle, address=address, org=org,
            kind=kind, registration=registration, updated=self.last_updated())

        # Return
        return result

    def contacts(self):
        """Get contact data.

        Args:
            None

        Returns:
            result: Contact object

        """
        # Initialize key variables
        Contact = namedtuple('Contact', 'name email kind status')
        results = []

        # Get entities from data
        entities = self._data['entities']
        for entity in entities:
            name = None
            email = None
            kind = None
            roles = entity.get('roles')
            status = entity.get('status')
            if bool(roles) and bool(status):
                if 'administrative' in roles and (
                        'validated' or 'active' in status):
                    # Get name and email
                    vcard = entity['vcardArray'][1]
                    for item in vcard:
                        if bool(item) is True:
                            if item[0] == 'fn':
                                name = item[-1]
                            if item[0] == 'email':
                                email = item[-1]
                            if item[0] == 'kind':
                                kind = item[-1]

                # Get name and email
                if bool(email):
                    results.append(Contact(
                        name=name, email=email, kind=kind, status=status[0]))

        # Return
        return results

    def last_updated(self):
        """Get the most recent time that any entity was updated.

        Args:
            None

        Returns:
            result: date

        """
        # Get all organization events
        all_events = self._data['events']
        dates = []
        result = None

        # Get related events
        keys = ['entities', 'autnums', 'networks']
        for key in keys:
            items = self._data.get(key)
            if bool(items) is True:
                for item in items:
                    events = item.get('events')
                    if bool(events) is True:
                        for event in events:
                            all_events.append(events)

        # Get the dates from events
        for event in all_events:
            date_ = event.get('eventDate')
            if bool(date_) is True:
                dates.append(date_)

        # Get the highest value date
        result = max(dates) if bool(dates) else None
        return result

    def everything(self):
        """Get combined data.

        Args:
            None

        Returns:
            result: OrgData object

        """
        # Initialize key variables
        OrgData = namedtuple(
            'OrgData', 'handle org address kind registration updated contacts')
        contacts = self.contacts()
        business = self.business()
        result = OrgData(
            handle=business.handle,
            org=business.org,
            address=business.address,
            kind=business.kind,
            registration=business.registration,
            updated=business.updated,
            contacts=contacts
        )
        return result


def main():
    """Main Function."""
    # Initialize key variables

    # Get the CLI arguments
    args = cli()

    # Log start
    log_message = 'Starting Job'
    log.log2debug(2000, log_message)

    # Get URLs from file
    filepath = os.path.abspath(os.path.expanduser(args.html_file))
    urls = get_urls(filepath)

    # Process Contact
    with open(args.output_file, 'w', newline='') as fh_:
        linewriter = csv.writer(
            fh_, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)

        # Create header row
        linewriter.writerow(
            ['business_org', 'business_address', 'business_handle',
             'business_kind', 'business_registration', 'business_updated',
             'contact_name', 'contact_email',
             'contact_kind', 'contact_status']
        )

        for url in urls:
            business = get_data(url)

            # Skip if business was invalid
            if bool(business) is False:
                continue

            # Process business
            for contact in business.contacts:
                # Log message
                log_message = 'Creating entry for {}'.format(contact.email)
                log.log2debug(2001, log_message)

                # Update file
                linewriter.writerow([
                    business.org,
                    business.address,
                    business.handle,
                    business.kind,
                    business.registration,
                    business.updated,
                    contact.name,
                    contact.email,
                    contact.kind,
                    contact.status,
                ])

                # Flush to disk immediately
                fh_.flush()
            break

    # Log stop
    log_message = 'Job complete'
    log.log2debug(2002, log_message)


def get_data(url):
    """Get data from URL.

    Args:
        url: URL.

    Returns:
        result: URL data

    """
    # Initialize key variables
    result = None
    html = None

    # Log
    log_message = 'Processing {}'.format(url)
    log.log2debug(2003, log_message)

    # Contientious sleep
    time.sleep(random.random() * 5)

    # Read data
    try:
        with urllib.request.urlopen(url) as response:
            html = response.read()

        if bool(html) is True:
            # Convert data to dict
            data = json.loads(html)
            org = Org(data)
            result = org.everything()
    except:
        pass

    print(result)

    # Return
    return result


def get_urls(filepath):
    """Extract URLs from file.

    Args:
        filepath: File to process.

    Returns:
        result: List of URLs

    """
    # Initialize key variables
    regex = re.compile(r'^(.*?)query=(.*?)&(.*?)$')
    codes = []
    result = []

    # Read html file
    with open(filepath) as fh_:
        lines = fh_.readlines()

    # Extract codes
    for line in lines:
        if 'https://search.ar''in.net/rdap?query' in line:
            # Extract code
            status = regex.match(line)
            if bool(status.group()):
                codes.append(status.group(2))

    # Create list of URLs
    for code in codes:
        result.append(
            'https://rdap.ar''in.net/registry/entity/{}'.format(code))

    # Randomly shuffle the URLs
    random.shuffle(result)
    return result


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
        '--html_file', type=str, required=True)
    parser.add_argument(
        '--output_file', type=str, required=True)

    # Parse and return
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()
