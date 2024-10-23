"""Application module to manage human file management."""

# Standard imports
import re

# PIP imports
import pandas as pd

# Library imports
from rain.Y2024.mailer import Person
from rain.Y2024 import misc


class _Humans():
    """Extract data from Organization."""

    def __init__(self):
        """Initialize the class.

        Args:
            None

        Returns:
            None

        """
        # Initialize key variables
        self._data = []

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

        # Return
        return result


class SimpleHumans(_Humans):
    """Extract data from Organization."""

    def __init__(self, filename):
        """Initialize the class.

        Args:
            filename: Name of tsv with humans

        Returns:
            None

        """
        # Initialize key variables
        _Humans.__init__(self)
        self._data = _simple_persons(filename)


class Humans(_Humans):
    """Extract data from Organization."""

    def __init__(self, filename):
        """Initialize the class.

        Args:
            filename: Name of tsv with humans

        Returns:
            None

        """
        # Initialize key variables
        _Humans.__init__(self)
        self._data = _persons(filename)


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
        self._strict_domains = [
            '.net', '.com', '.edu', '.us', '.co', '.cloud', '.io', '.fm'
        ]

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
            'Saint Kitts And Nevis', 'Saint Lucia', 'Virgin Islands, U.S.',
            'Saint Vincent And The Grenadines', 'Turks And Caicos Islands',
            'Virgin Islands, British']

        # Process and return
        for _country in countries:
            result.extend(self.country(_country))
        return result

    def country(self, _country, individuals_only=False):
        """Return all persons from a specific country.

        Args:
            _country: Country to select
            individuals_only: Only return individuals if True

        Returns:
            result: List of Persons from the country

        """
        # Initialize key variables
        result = []

        # Process and return
        for person in self._persons:
            if person.country == _country:
                if bool(individuals_only) is False:
                    result.append(person)
                else:
                    if person.individual is True:
                        result.append(person)
        return result

    def state(self, _state,
              individuals_only=False, timestamp=None, strict=False):
        """Return all persons from a specific state.

        Args:
            _state: Country to select
            individuals_only: Only return individuals if True
            timestamp: Filter by timestamps > this value if not None
            strict: Only privately held organizations if True. This uses very
                conservative criteria, '.com' and '.net' email TLDs

        Returns:
            result: List of Persons from the state

        """
        # Initialize key variables
        result = []

        # Process and return
        for person in self._persons:
            if person.state == _state:
                # Filter by email domain
                if bool(strict) is True:
                    if self._skip(person):
                        continue

                # Filter by timestamp
                if bool(timestamp) is True:
                    # print(person.organization_updated)
                    ts_updated = misc.timestamp(person.organization_updated)
                    if timestamp > ts_updated:
                        continue

                # Update the records
                if bool(individuals_only) is False:
                    result.append(person)
                else:
                    if person.individual is True:
                        result.append(person)
        return result

    def edu(self, individuals_only=False):
        """Return all persons related to educational institutions.

        Args:
            individuals_only: Only return individuals if True

        Returns:
            result: List of Persons

        """
        # Initialize key variables
        result = []

        # Process and return
        for person in self._persons:
            if person.email.lower().endswith('.edu'):
                # Update the records
                if bool(individuals_only) is False:
                    result.append(person)
                else:
                    if person.individual is True:
                        result.append(person)
        return result

    def smallfry(self, individuals_only=False, threshold=30, strict=False):
        """Return all persons related to educational institutions.

        Args:
            individuals_only: Only return individuals if True
            threshold: Only process states with at least this number of orgs.
            strict: Only privately held organizations if True.

        Returns:
            result: List of Persons

        """
        # Initialize key variables
        result = []

        # Get the histogram of persons
        lookup = histogram(self._persons, individuals_only=individuals_only)

        # Process data
        for person in self._persons:
            # Filter by email domain
            if bool(strict) is True:
                if self._skip(person):
                    continue

            # Append person to list if under the threshold for the state
            count = lookup.get(person.state)
            if bool(count) is True:
                if count <= threshold:
                    # Update the records
                    if bool(individuals_only) is False:
                        result.append(person)
                    else:
                        if person.individual is True:
                            result.append(person)
        # Return
        return result

    def _skip(self, person):
        """Determine whether the person should be skipped.

        Args:
            person: Person object

        Returns:
            result: True if they should be skipped

        """
        # Initialize key variables
        result = False

        # Filter by email domain
        domain = '.{}'.format(person.email.split('.')[-1])
        result = domain not in self._strict_domains
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
            'contact_email'].strip().lower() if bool(
                row['contact_email']) else None
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

        # Get type of person record
        contact_kind = row['contact_kind'].strip()

        # Add to dict
        if bool(email) is True:
            result.append(
                Person(
                    firstname=firstname.title(),
                    lastname=lastname.title(),
                    email=_fix_email(email),
                    individual=_is_individual(
                        firstname, lastname, email, contact_kind),
                    country=address[-1].title(),
                    state=address[-3].upper(),
                    validated=validated,
                    organization=row['business_org'],
                    organization_updated=row['business_updated']
                )
            )

    # Return
    return result


def _simple_persons(filename):
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
    df_['lastname'] = df_['Name'].str.split().str[-1]
    df_['firstname'] = df_['Name'].str.split().str[0]

    # Create Person objects
    for _, row in df_.iterrows():
        # Trim names
        firstname = row[
            'firstname'].strip() if bool(row['firstname']) else None
        lastname = row[
            'lastname'].strip() if bool(row['lastname']) else None
        email = row['Email'].strip().lower() if bool(row['Email']) else None

        # Skip unwanted email addresses
        if _email_ok(email) is False:
            continue

        # Add to dict
        if bool(email) is True:
            result.append(
                Person(
                    firstname=firstname.title(),
                    lastname=lastname.title(),
                    email=_fix_email(email),
                    individual=True,
                    country=None,
                    state=None,
                    validated=True,
                    organization=None,
                    organization_updated=None
                )
            )

    # Return
    return result


def _is_individual(firstname, lastname, email, contact_kind):
    """Determine whether this is a person or a department.

    Args:
        firstname: First name
        lastname: Last name
        company: Name of company
        email: Email address
        contact_kind: Kind of contact (individual, group)

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
        'ciso', 'office', 'operator', 'procure', 'register', 'notify', 'poc',
        'ipaddr', 'isp', 'pilot', 'company', 'peer', 'coord', 'info@',
        'scanning', 'routing', 'staff', 'internet', 'connect', 'allocation']
    names = ['abuse']

    # Check strings that should only appear in people and department names
    for item in departments:
        # Check typical department names
        if item.lower() in firstname.lower() or (
                item.lower() in lastname.lower()) or (
                    item.lower() in email.lower().split('@')[0]):
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

    # If the organization says that this is a group,
    # then it's not an individual
    if contact_kind.lower() == 'group':
        result = False

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


def _fix_email(email):
    """Remove '+' sign from email address.

    Args:
        email: Email address

    Returns:
        result: Fixed email address

    """
    # Initialize key variables
    result = email.lower().strip()

    # Return
    if '+' in email.lower().strip():
        result = '{}@{}'.format(email.split('+')[0], email.split('@')[-1])
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

    for bad_domain in bad_domains:
        components = domain.split('.')
        for component in components:
            if bad_domain.lower() == component.lower():
                result = False
                break

    # No 'ar''in' addresses
    if 'ar''in' in domain:
        result = False

    return result


def goats(humans_):
    """Generate mailtos for GOATs.

    Args:
        mailto: email.Thunderbird object
        persons: List of person objects

    Returns:
        None

    """
    # Initialize key variables
    counter = {}
    lookup = {}
    targets = []

    # Get all records
    everyone = humans_.complete()

    # Get frequency data and create lookup
    for person in everyone:
        email = person.email
        if counter.get(email):
            counter[email] += 1
            lookup[email].append(person)
        else:
            counter[email] = 1
            lookup[email] = [person]

    # Print result
    for email, count in sorted(
            counter.items(), key=lambda item: item[1], reverse=True):
        # print(email)
        if count > 1:
            print('{:<50}: {}'.format(email, count))

            # Get the most popular company name
            companies = [_.organization for _ in lookup[email]]
            most_popular = max(set(companies), key=companies.count)
            person = [
                _ for _ in lookup[email] if _.organization == most_popular][0]
            targets.append(person)

    # Update files
    return targets


def histogram(persons, individuals_only=False):
    """Analyze persons.

    Args:
        persons: List of Persons objects

    Returns:
        lookup: Dict keyed by state/province of organization counts

    """
    # Initialize key variables
    lookup = {}
    non_caribbean = []

    # All states except those near Washington DC (DC, MD, VA)
    states = [
        'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI',
        'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'ME', 'MI', 'MN',
        'MS', 'MO', 'MT', 'NC', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'ND',
        'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT',
        'WA', 'WV', 'WI', 'WY'
    ]

    # All provinces except those near Ottawa (QC)
    provinces = [
        'AB', 'BC', 'MB', 'NB', 'NL', 'NT', 'NS', 'NU', 'ON', 'PE', 'SK',
        'YT'
    ]
    non_caribbean.extend(states)
    non_caribbean.extend(provinces)

    # Process data
    for person in persons:
        if bool(individuals_only) is True and person.individual is False:
            continue
        if person.state in non_caribbean:
            found = lookup.get(person.state)
            if bool(found) is True:
                lookup[person.state] += 1
            else:
                lookup[person.state] = 1

    # Return
    return lookup
