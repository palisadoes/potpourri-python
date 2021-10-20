"""Application module to manage human file management."""

# Standard imports
import sys
import re

# PIP imports
import pandas as pd

# Library imports
from rain.mailer import Person


class Humans():
    """Extract data from Organization."""

    def __init__(self, filename):
        """Initialize the class.

        Args:
            filename: Name of tsv with humans

        Returns:
            None

        """
        # Initialize key variables
        self._data = _persons(filename)

    def complete(self):
        """Convert human email file to list of Person objects.

        Args:
            None

        Returns:
            result: List of Person objects

        """
        # Return
        return self._data

    def uniques(self):
        """Convert human email file to list of unique Person objects.

        Args:
            None

        Returns:
            result: List of Person objects

        """
        # Initialize key variables
        result = []
        uniques = {}

        # Create unique Person objects
        for person in self._data:
            # Add to dict
            if bool(person.email) is True:
                uniques[person.email] = person

        # Create a list of unique tuples
        for _, value in sorted(uniques.items()):
            result.append(value)
            print(value)
        sys.exit(0)

        # Return
        return result


class Strainer():
    """Extract data from Organization."""

    def __init__(self, persons):
        """Initialize the class.

        Args:
            persons: List of Person objects

        Returns:
            None

        """
        # Initialize key variables
        self._persons = persons

    def caribbean(self):
        """Return all Caribbean persons.

        Args:
            None

        Returns:
            result: List of Persons from the Caribbean

        """
        # Initialize key variables
        result = []
        countries = [
            'Anguilla', 'Antigua And Barbuda', 'Bahamas', 'Barbados',
            'Bermuda', 'Cayman Islands', 'Dominica', 'Grenada', 'Jamaica',
            'Saint Kitts And Nevis', 'Saint Lucia',
            'Saint Vincent And The Grenadines', 'Turks And Caicos Islands',
            'Virgin Islands, British']

        # Process and return
        for _country in countries:
            result.extend(self.country(_country))
        return result

    def country(self, _country):
        """Return all persons from a sprecific country.

        Args:
            _country: Country to select

        Returns:
            result: List of Persons from the country

        """
        # Initialize key variables
        result = []

        # Process and return
        for person in self._persons:
            if person.country == _country:
                result.append(person)
        return result

    def state(self, _state):
        """Return all persons from a sprecific state.

        Args:
            _state: Country to select

        Returns:
            result: List of Persons from the state

        """
        # Initialize key variables
        result = []

        # Process and return
        for person in self._persons:
            if person.state == _state:
                result.append(person)
        return result


def _persons(filename):
    """Convert human email file to list of Person objects.

    Args:
        filename: Name of tsv with humans

    Returns:
        result: List of Person objects

    """
    # Initialize key variables
    result = []
    df_ = pd.read_csv(filename, header=0, delimiter='\t')

    # Convert Nan to None
    df_ = df_.where(pd.notnull(df_), None)

    # Create 'firstname' and 'lastname' columns
    df_['lastname'] = df_['contact_name'].str.split().str[-1]
    df_['firstname'] = df_['contact_name'].str.split().str[0]

    # Create Person objects
    for _, row in df_.iterrows():
        # Skip if too old
        if _too_old(row['business_registration']):
            continue

        # Trim names
        firstname = row[
            'firstname'].strip() if bool(row['firstname']) else None
        lastname = row[
            'lastname'].strip() if bool(row['lastname']) else None
        email = row[
            'contact_email'].strip() if bool(row['contact_email']) else None
        validated = 'valid' in row['contact_status'].lower()

        # Skip this is a test account
        if 'test' in firstname.lower() or 'test' in lastname.lower():
            continue

        # Skip unwanted email addresses
        if _email_ok(email) is False:
            continue

        # Skip the obvious
        domain = email.split('@')[-1]
        if 'ar''in' in domain:
            continue

        # Get country and state information
        address = row['business_address'].split(':')

        # Add to dict
        if bool(email) is True:
            result.append(
                Person(
                    firstname=firstname.title(),
                    lastname=lastname.title(),
                    email=email.lower(),
                    individual=_is_individual(firstname, lastname, email),
                    country=address[-1].title(),
                    state=address[-3].upper(),
                    validated=validated
                )
            )

    # Return
    return result


def _is_individual(firstname, lastname, email):
    """Determine whether this is a person or a department.

    Args:
        firstname: First name
        lastname: Last name
        company: Name of company
        email: Email address

    Returns:
        result: True if individual

    """
    # Initialize key variables
    result = True
    departments = [
        'admin', 'master', 'network', 'noc', 'netops', 'contact', 'wireless',
        'operations', 'contact', 'support', 'dns', 'office', 'team', 'account',
        'group', 'dept', 'department', 'service', 'eng', 'address', 'llc',
        'information', 'security', 'cto', 'tech', 'telecom', 'center', 'chief',
        'number', 'division', 'manag', 'ar''in', 'ops', 'whois', 'ceo', 'test',
        'officer', 'cloud', 'president', 'owner', 'purchasing', 'help', 'desk',
        'infra', 'billing', 'ltd', 'partner', 'registr', 'albuquerque',
        'legal', 'corp', 'founder', 'domain', 'internet', 'analyst', 'licence',
        'ciso', 'office', 'operator', 'procure', 'register', 'notify',
        'ipaddr', 'isp', 'pilot', 'company', 'peer', 'coord',
        'scanning', 'routing', 'staff', 'internet', 'connect', 'allocation']
    names = ['abuse']

    # Check strings that should only appear in people and department names
    for item in departments:
        # Check typical department names
        if item.lower() in firstname.lower() or (
                item.lower() in lastname.lower()) or (
                    item.lower() in email.lower()):
            result = False
            break

        # Check if firstname and lastname match
        if firstname.lower() == lastname.lower():
            result = False
            break

        # Eliminate IT departments
        if firstname.lower() == 'it' or lastname.lower() == 'it':
            result = False
            break

        # Check if firstname is a single letter.
        # Can't be sure if it's individual or not.
        if len(re.sub('[^0-9a-zA-Z]+', '', firstname)) == 1:
            result = False
            break

    # Check strings that should only appear in people names
    for item in names:
        # Check typical names
        if item.lower() in firstname.lower() or (
                item.lower() in lastname.lower()):
            result = False
            break

    # Return
    return result


def _too_old(datestring, year='2000'):
    """Determine whether date is too old.

    Args:
        datestring: ISO 8601 time
        year: Minimum expected year

    Returns:
        result: True if too old

    """
    # Initialize key variables
    result = True

    # Return
    if bool(datestring):
        result = datestring < year
    return result


def _email_ok(email):
    """Check validity of email address.

    Args:
        email: Email address

    Returns:
        result: True if valid

    """
    # Initialize key variables
    result = True
    bad_domains = ['.gov', '.mil']
    domain = email.split('@')[-1]

    # Process and return
    for bad_domain in bad_domains:
        if domain.lower().endswith(bad_domain):
            result = False
            break

    # No 'ar''in' addresses
    if 'ar''in' in domain:
        result = False

    return result
