#!/usr/bin/env python3
"""Script to curate hashtags for Instagram posts."""

from __future__ import print_function

import os
import sys
from collections import namedtuple
import csv
import argparse
import random
import re
from operator import attrgetter
import textwrap


class Hashtags():
    """Class to evaluate file data."""

    def __init__(self, rows, limit=25):
        """Initialize the class.

        Args:
            rows: List of Row objects
            limit: The number of rows to select

        Returns:
            None

        """
        # Initalize key variables
        buckets = {}

        # Create buckets
        Bucket = namedtuple('Bucket', 'min max percent')
        Entry = namedtuple('Entry', 'size max percent')
        entries = [
            Entry(size='XXXL', max=1000000000, percent=3),
            Entry(size='XXL', max=1000000, percent=7),
            Entry(size='XL', max=500000, percent=55),
            # Entry(size='L', max=100000, percent=25),
            Entry(size='M', max=50000, percent=25),
            Entry(size='S', max=20000, percent=10),
            Entry(size='N/A', max=10000, percent=0)
        ]
        entries = sorted(entries, key=attrgetter('max'))
        for index, entry in enumerate(entries[:-1]):
            next_index = index + 1
            buckets[entries[next_index].size] = Bucket(
                min=entry.max,
                max=entries[next_index].max,
                percent=entries[next_index].percent)

        # Get rows
        self.rows = _select(rows, buckets, limit=limit)


class FeatureHashtags(Hashtags):
    """Class to evaluate file data for feature account hashtags."""

    def __init__(self, rows, limit=25):
        """Initialize the class.

        Args:
            rows: List of Row objects
            limit: The number of rows to select

        Returns:
            None

        """
        # Instantiate
        _rows = [row for row in rows if row.feature is True]
        Hashtags.__init__(self, _rows, limit=limit)


class RegularHashtags(Hashtags):
    """Class to evaluate file data for regular hashtags."""

    def __init__(self, rows, limit=25):
        """Initialize the class.

        Args:
            rows: List of Row objects
            limit: The number of rows to select

        Returns:
            None

        """
        # Instantiate
        _rows = [row for row in rows if row.feature is False]
        Hashtags.__init__(self, _rows, limit=limit)


def _select(rows, buckets, limit=25):
    """Process data.

    Args:
        rows: List of Row objects obtained from file
        buckets: Buckets for classifying rows
        limit: Maximum number of results

    Returns:
        selected: List of selected rows

    """
    # Initalize key variables
    results = {}
    selected = []
    max_iter = 5000

    # Select rows according to the bucket requirements
    for size, bucket in buckets.items():
        # Initialize result for bucket
        results[size] = []
        count = 0

        # Get the required number of items per bucket
        required = limit * bucket.percent / 100

        while len(results[size]) < required:
            # Exit if insufficient items found
            count += 1
            if count > max_iter:
                break

            # Randomly select row
            row = random.choice(rows)

            # Check if row is within the bucket range and if so, add
            if bucket.min <= row.posts <= bucket.max:
                found = bool(results.get(size))
                if found:
                    if row not in results[size]:
                        results[size].append(row)
                else:
                    results[size].append(row)

    # Create a list of selected rows
    for value in results.values():
        selected.extend(value)

    # Return
    selected = sorted(selected, key=attrgetter('posts'), reverse=True)
    return selected


def main():
    """Process data.

    Args:
        None

    Returns:
        None

    """
    # Initialize key variables
    Row = namedtuple('Row', 'hashtag posts feature')
    rows = []
    args = _args()
    filename = os.path.expanduser(args.filename)
    limit = abs(args.results)
    percent = abs(args.percent)
    verbose = args.verbose
    additions = _additions(args.additions)

    # Add limits to the CLI parameters
    percent = percent if 0 <= percent <= 100 else 25
    limit = limit if 10 <= limit < 30 else 25

    # Process destination
    if os.path.isfile(filename) is False:
        print('Filename "{}" does not exist.'.format(filename))
        sys.exit(0)

    # Read CSV file
    with open(filename, newline='') as fh_:
        reader = csv.DictReader(fh_, delimiter='\t')
        for row in reader:
            rows.append(
                Row(
                    hashtag=row['Hashtag'].lower().strip(),
                    posts=abs(int(row['Posts'].strip().replace(',', ''))),
                    feature=bool('f' in row['Type'].lower())
                )
            )

    # Create report
    report(rows, limit=limit, feature_percent=percent,
           additions=additions, verbose=verbose)


def report(rows, limit=25, feature_percent=25, additions=None, verbose=False):
    """Process data.

    Args:
        rows: List of Row objects
        limit: The number of rows to select
        feature_percent: Percentage of hashtags from feature accounts
        additions: List of hashtags to add
        verbose: Verbose output if True

    Returns:
        None

    """
    # Initialize key variables
    results = []
    hashtags = []
    width = 100

    # Get results for both hashtag types
    features = FeatureHashtags(rows, limit=limit).rows
    regulars = RegularHashtags(rows, limit=limit).rows

    results.extend(random.sample(
        regulars, int(len(regulars) * (1 - (feature_percent / 100)))))
    results.extend(random.sample(
        features, int(len(features) * feature_percent / 100)))

    # Select alternating tags
    results = sorted(results, key=attrgetter('posts'), reverse=True)
    for result in results:
        hashtags.append(result.hashtag)
        if bool(verbose) is True:
            print(result)

    # Add any additionally requested hashtags
    if isinstance(additions, list):
        for addition in additions:
            if isinstance(addition, str):
                if addition.startswith('#'):
                    hashtags.insert(0, addition)

    # Trim hashtag list after additions
    hashtags = hashtags[:limit]

    # Shuffle hashtags to hide methodology
    random.shuffle(hashtags)

    # Print results
    output = textwrap.wrap(' '.join(hashtags), width, break_long_words=False)
    print('\n{}{}\n'.format('.\n' * 5, '\n'.join(output)))


def _additions(additions):
    """Create list of additional hashtags to use.

    Args:
        additions

    Returns:
        result: List of hashtags

    """
    # Initialize key variables
    result = []

    if bool(additions) is True:
        # Split on word boundaries, including commas
        hashtags = re.findall(r"[\w']+", additions)

        # Add hashtags
        for hashtag in hashtags:
            if bool(re.match(r'^\w+$', hashtag).group(0)) is True:
                result.append('#{}'.format(hashtag.lower()))

    # Return
    return result


def _args():
    """Get the CLI arguments.

    Args:
        None

    Returns:
        result: Args dictionary

    """
    # Process CLI options
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--filename',
        type=str,
        required=True,
        help='Name of file to process.')
    parser.add_argument(
        '--percent',
        type=int,
        required=False,
        default=25,
        help='Percent of results that are feature accounts.')
    parser.add_argument(
        '--additions',
        type=str,
        required=False,
        help='List of mandatory hashtags to add.')
    parser.add_argument(
        '--results',
        type=int,
        required=False,
        default=25,
        help='Number of results to return.')
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='increase output verbosity')
    result = parser.parse_args()
    return result


if __name__ == "__main__":
    main()
