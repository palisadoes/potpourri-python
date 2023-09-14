#!/usr/bin/env python3
"""Script to resize photos for Instagram."""

from __future__ import print_function

import os
import sys
from collections import namedtuple
import argparse
from operator import attrgetter
from multiprocessing import get_context
import csv
import time
import shutil
import statistics


from PIL import Image

Shade = namedtuple("Shade", "filepath shade square")
Batch = namedtuple("Batch", "filepath shade batch square")


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
    input_directory = os.path.expanduser(args.input_directory)
    output_directory = os.path.expanduser(args.output_directory)
    report_filename = os.path.expanduser(args.report_filename)
    parallel = args.parallel
    batches = args.batches

    # Process source
    if os.path.isdir(input_directory) is False:
        print(
            """\
Source directory '{}' does not exist.""".format(
                input_directory
            )
        )
        sys.exit(0)

    # Process destination
    if os.path.isdir(input_directory) is False:
        print(
            """\
Destination directory '{}' does not exist.""".format(
                input_directory
            )
        )
        sys.exit(0)

    # Get filepaths
    filepaths = _filepaths(input_directory)

    # Process
    evaluations = _evaluate(filepaths, parallel=parallel, batches=batches)
    batched_evaluations = _batch(evaluations, batches=batches)
    _report(batched_evaluations, report_filename)
    if bool(output_directory) is True:
        _librarian(batched_evaluations, output_directory)

    # Get a clear CLI prompt
    print(
        "Processed : {1} files\nDuration  : {0}s\nOutput    : {2}".format(
            round(time.time() - start, 2), len(evaluations), report_filename
        )
    )


def _librarian(records, output_directory):
    """Make copies of files according to their batch number.

    Args:
        records: List of Batch objects
        output_directory: Name of root directory into which to put the files

    Returns:
        None

    """
    # Copy files
    for record in records:
        # Create batch directory tree if necessary
        batch_directory = "{0}{1}photo_book{1}{2}".format(
            output_directory, os.sep, str(record.batch).zfill(3)
        )
        if os.path.isdir(batch_directory) is False:
            os.makedirs(batch_directory, exist_ok=True)

        dst = "{}{}{}".format(
            batch_directory, os.sep, os.path.basename(record.filepath)
        )
        shutil.copyfile(record.filepath, dst)


def _report(records, output_filename):
    """Evaluate the shading of files.

    Args:
        records: List of Batch objects
        output_filename: Name of file for output

    Returns:
        results: List of Shade objects

    """
    # Create the CSV file
    with open(output_filename, "w") as fh_:
        writer = csv.writer(fh_, delimiter=",")
        writer.writerow(["Batch", "Filename", "Shade", "Square"])

        # Write file data
        for record in records:
            writer.writerow(
                [
                    record.batch,
                    os.path.basename(record.filepath),
                    record.shade,
                    "Yes" if bool(record.square) else "No",
                ]
            )


def _batch(items, batches=10):
    """Create batches of records for processing.

    Args:
        items: List of Shade objects

    Returns:
        results: List of Batch objects

    """
    # Initialize key variables
    MinMax = namedtuple("MinMax", "min max")
    records = sorted(items, key=attrgetter("shade"))
    results = []
    ranges = [MinMax(min=_ - 1, max=_) for _ in list(range(1, batches + 1))]

    # Process records
    for record in records:
        for key, value in enumerate(ranges):
            if value.min < record.shade <= value.max:
                # Update batch information
                results.append(
                    Batch(
                        filepath=record.filepath,
                        shade=record.shade,
                        batch=key + 1,
                        square=record.square,
                    )
                )

    # Return
    return results


def _evaluate(filepaths, parallel=True, batches=10):
    """Evaluate the shading of files.

    Args:
        filepaths: List of filepaths to evaluate
        parallel: Use parallel processing if True
        batches: Number of batches for the grouping

    Returns:
        results: List of Shade objects

    """
    # Initialize key variables
    results = []
    cores = int(os.cpu_count() * 0.8)

    # Process the filepaths
    if bool(parallel) is True:
        with get_context("spawn").Pool(processes=cores) as pool:
            arguments = [(filepath, batches) for filepath in filepaths]
            results = pool.starmap(_shading, arguments)
    else:
        for filepath in filepaths:
            listing = _shading(filepath)
            if bool(listing) is True:
                results.extend(listing)

    # Return
    return results


def _shading(filepath, batches=10):
    """Evaluate the shading of files.

    Args:
        filepath: File to evaluate
        batches: Number of batches for the grouping

    Returns:
        result: Value of Shade

    """
    # Initialize key variables
    RGB = namedtuple("RGB", "red blue green")
    image = Image.open(filepath)
    pixels = image.load()
    shades = []

    # Process the file
    for row in range(image.width):
        for column in range(image.height):
            # Try block to protect against bad metadata
            try:
                rgb = pixels[column, row]
            except:
                continue

            pixel = RGB(red=rgb[0], blue=rgb[1], green=rgb[2])

            # Ignore pure white, which could be a border
            if pixel == RGB(red=255, blue=255, green=255):
                continue

            # Calculate the mean value
            shades.append(
                statistics.mean([pixel.red, pixel.blue, pixel.green])
            )

    # Make shade value between 0 and 10
    shade = round(statistics.mean(shades) / (255 / batches), 2)
    return Shade(
        filepath=filepath, shade=shade, square=image.width == image.height
    )


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
        filepath = "{}{}{}".format(source, os.sep, filename)
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
    FileType = namedtuple("FileType", "jpg unsupported")
    result = FileType(jpg=False, unsupported=True)

    # Determine the type of file
    if filepath.lower().endswith(".jpg") is True or (
        filepath.lower().endswith(".jpeg") is True
    ):
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
        "--input_directory",
        required=True,
        type=str,
        help="Directory containing JPG files to process.",
    )
    parser.add_argument(
        "--output_directory",
        default="",
        type=str,
        help="Directory where batched JPG files will be copied.",
    )
    parser.add_argument(
        "--report_filename",
        type=str,
        default="/tmp/bw_jpg_shade_ranking.csv",
        help="CSV file for results.",
    )
    parser.add_argument(
        "--batches",
        type=int,
        default=10,
        help="Number of batches to create. Default = 10",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Use multiprocessing.",
    )
    result = parser.parse_args()
    return result


if __name__ == "__main__":
    main()
