#!/usr/bin/env python3
"""Script to resize photos for Instagram."""

from __future__ import print_function

import os
import sys
from collections import namedtuple
import argparse
from operator import attrgetter
from multiprocessing import Pool
import csv
import time

from PIL import Image

Shade = namedtuple('Shade', 'filepath shade')


def main():
    """Process data.

    Args:
        None

    Returns:
        None

    """
    # Initialize key variables
    filepaths = []
    start = time.time()
    args = _args()
    directory = os.path.expanduser(args.directory)
    output_filename = os.path.expanduser(args.output_filename)

    # Process destination
    if os.path.isdir(directory) is False:
        print('''\
Destination directory '{}' does not exist.'''.format(directory))
        sys.exit(0)

    # Get filepaths
    filepaths = _filepaths(directory)

    # Process
    evaluations = _evaluate(filepaths)
    _report(evaluations, output_filename)

    # Get a clear CLI prompt
    print('Processed : {1} files\nDuration  : {0}s\nOutput    : {2}'.format(
        round(time.time() - start, 2), len(evaluations), output_filename)
        )


def _report(evaluations, output_filename):
    """Evaluate the shading of files.

    Args:
        evaluations: List of evaluated Shade objects
        output_filename: Name of file for output

    Returns:
        results: List of Shade objects

    """
    # Initialize key variables
    results = sorted(evaluations, key=attrgetter('shade'))
    tenth = int(len(results) / 10)
    count = 0
    batch = 0

    # Create the CSV file
    with open(output_filename, 'w') as fh_:
        writer = csv.writer(fh_, delimiter=',')
        writer.writerow(['Batch', 'Filename', 'Shade'])

        for result in results:
            # Write the batch number
            if count == 0:
                batch += 1

            # Write file data
            writer.writerow(
                [batch, os.path.basename(result.filepath), result.shade])
            count += 1

            # Reset the count
            if count == tenth:
                count = 0


def _evaluate(filepaths):
    """Evaluate the shading of files.

    Args:
        filepaths: List of filepaths to evaluate

    Returns:
        results: List of Shade objects

    """
    # Initialize key variables
    results = []
    cores = int(os.cpu_count() * 0.8)

    # Process the filepaths
    with Pool(processes=cores) as pool:
        tuples = pool.map(_shading, filepaths)

    # Return
    results = [Shade(filepath=_[0], shade=_[1]) for _ in tuples]
    return results


def _shading(filepath):
    """Evaluate the shading of files.

    Args:
        filepath: File to evaluate

    Returns:
        result: Value of shading

    """
    # Initialize key variables
    RGB = namedtuple('RGB', 'red blue green')
    image = Image.open(filepath)
    pixels = image.load()
    shades = []

    # Process image
    for row in range(image.width):
        for column in range(image.height):
            rgb = pixels[column, row]
            pixel = RGB(red=rgb[0], blue=rgb[1], green=rgb[2])

            # Ignore pure white, which could be a border
            if pixel == RGB(red=255, blue=255, green=255):
                continue

            # Calculate the mean value
            shades.append(
                _shade([pixel.red, pixel.blue, pixel.green])
            )

    # Make shade value between 0 and 10
    shade = round(_shade(shades) / 25.5, 2)
    return (filepath, shade)


def _shade(values, decimals=2):
    """Get shade value.

    Args:
        values: List of shade values
        decimals: Decimal place rounding

    Returns:
        result: Mean shade value

    """
    mean = sum(values) / len(values)
    result = round(mean, decimals)
    return result


def _filepaths(source):
    """Get valid file paths for processing.

    Args:
        source: Source directory

    Returns:
        result: List of valid filepaths

    """
    # Initialize key variables
    result = []

    # Get a list of files
    files = os.listdir(source)
    for filename in sorted(files):
        # Only interested in files
        filepath = '{}{}{}'.format(source, os.sep, filename)
        if _valid_file(filepath) is True:
            result.append(filepath)

    # Return
    return result


def _valid_file(filepath):
    """Validate filepath.

    Args:
        filepath: filepath

    Returns:
        result: True if a valid file

    """
    # Initialize key variables
    result = False

    # Get a list of files
    if os.path.isfile(filepath) is True:
        # We are only interested in JPG
        filetype = _filetype(filepath)
        if filetype.unsupported is False:
            result = True

    # Return
    return result


def _filetype(filepath):
    """Determine type of file.

    Args:
        filepath: Name of file

    Returns:
        result: True if JPG

    """
    # Initialize key variables
    FileType = namedtuple('FileType', 'jpg unsupported')
    result = FileType(jpg=False, unsupported=True)

    # Determine the type of file
    if filepath.lower().endswith('.jpg') is True or (
            filepath.lower().endswith('.jpeg') is True):
        result = FileType(jpg=True, unsupported=False)
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
        '--directory',
        required=True,
        type=str,
        help='Directory containing JPG files to process.')
    parser.add_argument(
        '--output_filename',
        type=str,
        default='/tmp/bw_jpg_shade_ranking.csv',
        help='CSV file for results.')
    result = parser.parse_args()
    return result


if __name__ == "__main__":
    main()
