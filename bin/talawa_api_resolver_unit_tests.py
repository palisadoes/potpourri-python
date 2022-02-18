#!/usr/bin/env python3
"""Script to generate the text and subjects for resolver unit test issues."""

from __future__ import print_function
import argparse
import os
from collections import namedtuple


def main():
    """Create the test APP for flask.

    Args:
        None

    Returns:
        app: Flask object

    """
    # Initialize key variables
    repo = 'talawa-api'
    Data = namedtuple('Data', 'filename directory count')

    # Process CLI
    count = 0
    args = _cli()
    root = os.path.abspath(args.directory)
    offset = root.find(repo) + len(repo) + 1

    # Get a recursive listing of files
    for directory, _, filenames in os.walk(root):
        for filename in filenames:
            count += 1
            data = Data(
                directory=directory[offset:], filename=filename, count=count)
            _print(data)


def _print(data):
    """Print output.

    Args:
        data: Data object

    Returns:
        None

    """
    # Print output
    print('\nSubject: Issue {}\n'.format(data.count))
    print(_subject(data))
    print('\n<!-- Body -->\n')
    print(_issue(data))
    input('')
    os.system('clear')


def _subject(data):
    """Create text for the issue's subject.

    Args:
        data: Data object

    Returns:
        result: Subject text

    """
    # Initialize key variables
    template = 'Unittests for FILE'
    result = template.replace('FILE', data.filename)
    return result


def _issue(data):
    """Create text for the issue's body.

    Args:
        data: Data object

    Returns:
        result: Body text

    """
    # Initialize key variables
    template = '''\
The Talawa-API code base needs to be 100% reliable. This means we need to have 100% unittest code coverage.

We will need unittests done for all methods, classes and/or functions found in this file.

`FILE`

This file can be found in the `DIRECTORY` directory

Parent Issue:
- https://github.com/PalisadoesFoundation/talawa/issues/1217

### PR Acceptance Criteria

- When complete this file must show **100%** coverage when merged into the code base.
- [The current code coverage for the file can be found here](https://codecov.io/gh/PalisadoesFoundation/talawa-api/tree/develop/DIRECTORY)
- The PR will show a report for the code coverage for the file you have added. You can use that as a guide.

'''
    result = template.replace(
        'FILE', data.filename).replace('DIRECTORY', data.directory)
    return result


def _cli():
    """Parse the CLI.

    Args:
        args: None

    Returns:
        args: ArgumentParser

    """
    # Initialize key variables
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--directory', type=str, required=True)

    # Parse and return
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
