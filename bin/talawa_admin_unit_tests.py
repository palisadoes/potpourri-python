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
    repo = 'talawa-admin'
    Data = namedtuple('Data', 'filename directory count')

    # Process CLI
    count = 0
    args = _cli()

    # Remove duplicates from the list of directories
    roots = list(
        set(
            [os.path.abspath(_) for _ in args.directories]
        )
    )

    # Get a recursive listing of files
    for root in sorted(roots):
        # Create an offset
        offset = root.find(repo) + len(repo) + 1

        for directory, _, filenames in os.walk(root):
            for filename in filenames:
                # Ignore test filenames
                if '.test.' in filename.lower():
                    continue

                # Ignore non TypeScript files
                if filename.lower().endswith('.tsx') or (
                        filename.lower().endswith('.ts')):
                    count += 1
                    data = Data(
                        directory=directory[offset:],
                        filename=filename, count=count)
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
    template = 'Code Coverage: Create tests for FILE'
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
The Talawa-Admin code base needs to be 100% reliable. This means we need to have 100% test code coverage.

Tests need to be written for file `SOURCE_DIRSOURCE_FILE`

- When complete, all methods, classes and/or functions in the file will need to be tested.
- These tests must be placed in a single file with the name `TEST_FILE`. You may need to create the appropriate directory structure to do this.

### IMPORTANT:
Please refer to the parent issue on how to implement these tests correctly:

- #241

### PR Acceptance Criteria

- When complete this file must show **100%** coverage when merged into the code base. This will be clearly visible when you submit your PR.
- [The current code coverage for the file can be found here](https://codecov.io/gh/PalisadoesFoundation/talawa-admin/tree/develop/SOURCE_DIR). If the file isn't found in this directory, or there is a 404 error, then tests have not been created.
- Create a code coverage account for your repo's preferred branch to generate the values when you do your commits for that branch to your repo.
    - _**NOTE:**_ Make sure you select the correct branch when you do the setup, or else the reporting will fail. You must also create a `CODECOV` GitHub secret for your repo as part of the process.
- The PR will show a report for the code coverage for the file you have added. You can also use that as a guide.

'''
    # Create TEST directory
    test_dir = data.directory
    test_file = '{}{}{}.test.{}'.format(
        test_dir,
        os.sep,
        '.'.join(data.filename.split('.')[:-1]),
        '.'.join(data.filename.split('.')[-1:]))

    # Create the body of the GitHub issue
    result = template.replace(
        'SOURCE_FILE', data.filename).replace(
            'SOURCE_DIR', '{}{}'.format(data.directory, os.sep)).replace(
                'TEST_FILE', test_file)

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
        '--directories', type=str, required=True, nargs='+')

    # Parse and return
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
