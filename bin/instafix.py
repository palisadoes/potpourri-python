#!/usr/bin/env python3
"""Script to resize photos for Instagram."""

from __future__ import print_function

import os
import sys
from collections import namedtuple
import argparse

from PIL import Image, ImageOps
import piexif


def main():
    """Process data.

    Args:
        None

    Returns:
        None

    """
    # Initialize key variables
    filepaths = []
    args = _args()
    destination = os.path.expanduser(args.destination)

    # Process destination
    if os.path.isdir(destination) is False:
        print('''\
Destination directory '{}' does not exist.'''.format(destination))
        sys.exit(0)

    # Process source
    if bool(args.source) is True:
        # Error if no directory
        source = os.path.expanduser(args.source)
        if os.path.isdir(source) is False:
            print(
                '''Source directory '{}' does not exist.'''.format(source))
            sys.exit(0)

        # Get filepaths
        filepaths = _filepaths(source)

    elif bool(args.filename) is True:
        filename = os.path.expanduser(args.filename)
        # Error if no file
        if os.path.isfile(filename) is False:
            print(
                '''Source filename '{}' does not exist.'''.format(filename))
            sys.exit(0)

        if _valid_file(filename) is True:
            filepaths = [filename]

    # Process
    _instagram(filepaths, destination)


def _instagram(filepaths, destination):
    """Process files for instagram.

    Args:
        filepaths: List of filepaths
        destination: Destination directory name

    Returns:
        None

    """
    # Initialize key variables
    ig_width = 1080
    border = 20
    quality = 100

    # Error if no directory
    if os.path.isdir(destination) is False:
        print('''\
Destination directory '{}' does not exist.'''.format(destination))
        sys.exit(0)

    for filepath in filepaths:
        # Create background image
        background = Image.new(
            'RGB', (ig_width, ig_width), color='white')

        # Resize source image to fit on background. Add a border
        original = _new_dimensions(
            filepath, ig_width=ig_width, border=border)
        resized = original.image.resize(
            (original.width, original.height), Image.ANTIALIAS)
        resized = ImageOps.expand(resized, border=1)

        # Set exif metadata to match the original except for the dimensions
        found = bool(original.image.info.get('exif'))
        if found is True:
            exif = piexif.load(original.image.info['exif'])
            exif['0th'][piexif.ImageIFD.ImageWidth] = original.width
            exif['0th'][piexif.ImageIFD.ImageLength] = original.height
            exif['0th'][piexif.ImageIFD.Artist] = 'Peter Harrison'
            exif['0th'][piexif.ImageIFD.Copyright] = (
                'ALL RIGHTS RESERVED - Peter Harrison @ SIMIYA.COM')

        # Overlay source image on background and save
        background.paste(
            resized, (original.hoffset, original.voffset))
        newfile = '{}{}Final-{}'.format(
            destination, os.sep, os.path.basename(filepath))
        newfile = newfile.replace('{0}{0}'.format(os.sep), os.sep)
        print('Converting {} to {}'.format(filepath, newfile))
        if found is True:
            background.save(newfile, quality=quality, exif=piexif.dump(exif))
        else:
            background.save(newfile, quality=quality)

        # Close redimensioned image
        original.image.close()


def _new_dimensions(filepath, ig_width=1024, border=20):
    """Return the desired dimensions of the image file.

    Args:
        filepath: Name of file
        ig_width: Width of the instagram photo
        border: Border we want around the final photo

    Returns:
        result: Dimensions object

    """
    # Initialize key variables
    reduction = 1
    Dimensions = namedtuple(
        'Dimensions', 'width height image hoffset voffset')
    inner_width = abs(ig_width) - abs(border)
    shim = int(abs(border) / 2)

    # Get image metadata
    image = Image.open(filepath)
    (_width, _height) = image.size
    max_dimension = max(_height, _width)

    # Determine the desired new dimensions
    if max_dimension > inner_width:
        reduction = inner_width / max_dimension

    # Calculate new width
    width = int(_width * reduction)
    height = int(_height * reduction)
    hoffset = int((inner_width - width) / 2) + shim
    voffset = int((inner_width - height) / 2) + shim

    # Return
    result = Dimensions(
        width=width,
        height=height,
        hoffset=hoffset,
        voffset=voffset,
        image=image)
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
        '--source',
        type=str,
        help='Directory containing files to process.')
    parser.add_argument(
        '--filename',
        type=str,
        help='Name of file to process.')
    parser.add_argument(
        '--destination',
        type=str,
        default='~/Pictures/instagram',
        help='Directory where output photos will reside.')
    result = parser.parse_args()
    return result


if __name__ == "__main__":
    main()
