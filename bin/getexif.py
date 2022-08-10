#!/usr/bin/env python3
"""Script to get exif data from JPG file."""

from __future__ import print_function

import os
import sys
from collections import namedtuple
import argparse

from PIL import Image
from PIL.ExifTags import TAGS
import piexif


def main():
    """Process data.

    Args:
        None

    Returns:
        None

    """
    # Initialize key variables
    filepath = None
    args = _args()

    if bool(args.filename) is True:
        filename = os.path.expanduser(args.filename)
        # Error if no file
        if os.path.isfile(filename) is False:
            print(
                """\
Source filename '{}' does not exist.""".format(
                    filename
                )
            )
            sys.exit(0)

        # Process
        if _valid_file(filename) is True:
            filepath = os.path.abspath(filename)
            _process(filepath)


def _process(filepath):
    """Process exif data.

    https://exiftool.org/TagNames/EXIF.html has a full list of tags

    Args:
        filepath: Filepath

    Returns:
        None

    """
    # Initialize key variables
    result = {}

    dict_list = _image(filepath)
    dict_list.extend(_zeroth(filepath))
    dict_list.extend(_exif(filepath))

    # Process data
    for item in dict_list:
        for key, value in item.items():
            result[key] = value

    # Print data
    for key, value in sorted(result.items()):
        print(f"{key:25}: {value}")


def _exif(filepath):
    """Process exif data.

    https://exiftool.org/TagNames/EXIF.html has a full list of tags

    pprint(TAGS) to get a full list known to the package

    Args:
        filepath: Filepath

    Returns:
        None

    """
    # Initialize key variables
    result = []
    meta = None

    # Read data
    with Image.open(filepath) as image:
        # Get all Exif. The '0th', '1st' and 'Exif' sections of the spec
        exifdata = image.info.get("exif")
        if bool(exifdata):
            meta = piexif.load(exifdata)

    # Process data
    if bool(meta) is True:
        for ifd in ("0th", "Exif", "GPS", "1st"):
            for tag in meta[ifd]:
                label = piexif.TAGS[ifd][tag]["name"]
                value = meta[ifd][tag]
                print(label, value)
                if isinstance(value, bytes):
                    try:
                        value = value.decode()
                    except:
                        continue

                # Fixup
                if label == "ExposureTime":
                    value = "{}/{}".format(value[0], value[1])
                if label == "FNumber":
                    value = float(value[0] / value[1])

                result.append({label: value})

    # Return
    return result


def _image(filepath):
    """Get basic image data from file.

    Args:
        filepath: Filepath

    Returns:
        result: List of image data dicts

    """
    # Initialize key variables
    result = []

    # Read data
    with Image.open(filepath) as image:
        # Extract image metadata
        lookup = {
            "Filename": image.filename,
            "Image Size": image.size,
            "Image Height": image.height,
            "Image Width": image.width,
            "Image Format": image.format,
            "Image Mode": image.mode,
            "Image is Animated": getattr(image, "is_animated", False),
            "Frames in Image": getattr(image, "n_frames", 1),
        }

    # Process data
    for label, value in lookup.items():
        result.append({label: value})
    return result


def _zeroth(filepath):
    """Extract a subset of the EXIF data. The '0th' section of the spec.

    https://exiftool.org/TagNames/EXIF.html has a full list of tags

    Args:
        filepath: Filepath

    Returns:
        result: List of image data dicts

    """
    # Initialize key variables
    result = []

    # Read data
    with Image.open(filepath) as image:
        # Extract a subset of the EXIF data.
        # The '0th' section of the specification
        zeroth = image.getexif()

    # Process data
    for tag_id in zeroth:
        # Get the tag name, instead of human unreadable tag id
        tag = TAGS.get(tag_id, tag_id)
        value = zeroth.get(tag_id)

        # Decode bytes
        if isinstance(value, bytes):
            try:
                value = value.decode()
            except:
                value = None

        if bool(value):
            result.append({"0th {}".format(tag): value})

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
        "--filename", type=str, help="Name of file to process."
    )
    result = parser.parse_args()
    return result


if __name__ == "__main__":
    main()
