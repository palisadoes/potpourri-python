#!/usr/bin/env python3
"""Script to curate hashtags for Instagram posts."""

from __future__ import print_function

import os
import sys
from collections import namedtuple
import csv
import argparse
import random


class Evaluate():
    """Class to evaluate file data."""

    def __init__(self, rows, limit=25):
        """Initialize the class.

        Args:
            rows: List of Row objects

        Returns:
            None

        """
        # Initalize key variables
        Bucket = namedtuple('Bucket', 'min max percent')
        result = {}
        selected = []
        self._buckets = {
            'XXL': Bucket(max=None, min=1000000, percent=3),
            'XL': Bucket(max=999999, min=5000000, percent=7),
            'L': Bucket(max=499999, min=100000, percent=30),
            'M': Bucket(max=99999, min=50000, percent=25),
            'S': Bucket(max=49999, min=20000, percent=25),
            'T': Bucket(max=19999, min=0, percent=10)
        }

        while True:
            row = random.choice(rows)
            
        num_rows = len(rows)
        for row in rows:
            pass


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
                    hashtag=row['Hashtag'].lower(),
                    posts=int(row['Posts'].replace(',', '')),
                    feature=bool('f' in row['Type'].lower())
                )
            )
    # print(random.choice(rows))


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
    result = parser.parse_args()
    return result


if __name__ == "__main__":
    main()
