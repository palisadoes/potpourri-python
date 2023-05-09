#!/usr/bin/env python3
"""Script to get exif data from JPG file."""

from __future__ import print_function

import os
import sys
from collections import namedtuple
import argparse
import hashlib
import shutil

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
    args = _args()

    if bool(args.source) is True:
        source = os.path.expanduser(args.source)
        # Error if no file
        if os.path.isdir(source) is False:
            print(
                """\
Source directory '{}' does not exist.""".format(
                    source
                )
            )
            sys.exit(0)

        if bool(args.destination) is True:
            destination = os.path.expanduser(args.destination)
            # Error if no file
            if os.path.isdir(destination) is False:
                print(
                    """\
Destination directory '{}' does not exist.""".format(
                        destination
                    )
                )
                sys.exit(0)

        # Process
        _process(source, destination)


def _process(source, destination):
    """Process data.

    Args:
        source: Root directory to process
        destination: Destination to place file with EXIF data

    Returns:
        None

    """
    # Get a recursive listing of files
    for directory, _, filenames in os.walk(source):
        for filename in filenames:
            in_filepath = "{}{}{}".format(directory, os.sep, filename).replace(
                "{0}{0}".format(os.sep), os.sep
            )

            if bool(in_filepath) is True:
                # Error if no file
                if os.path.isfile(in_filepath) is False:
                    print("Filename '{}' does not exist.".format(in_filepath))
                    continue

                # Process
                if _valid_file(in_filepath) is True:
                    data = _metadata(in_filepath)

                    # Compatible with Rapid Photo Downloader?
                    compatible = data.get("Model")
                    if bool(compatible) is True:
                        print(
                            f"""\
{in_filepath:25}: Model: {compatible:25}: {bool(compatible)}"""
                        )

                        # Get the extension
                        (_, extension) = in_filepath.split(".")

                        # Get the out_filepath
                        digest = _digest(in_filepath)
                        if bool(digest) is True:
                            out_filepath = "{}{}{}.{}".format(
                                destination, os.sep, digest, extension
                            ).replace("{0}{0}".format(os.sep), os.sep)

                            print(f"""Creating: {out_filepath:25}""")
                            shutil.move(in_filepath, out_filepath)

                    else:
                        print(
                            f"""\
{in_filepath:25}: Model: {'None':25}: {bool(compatible)}"""
                        )


def _digest(filepath):
    """Get the HEX digest of file.

    Args:
        filepath: File path

    Returns:
        result: Hex digest

    """
    # Return
    result = None
    with open(filepath, "rb") as fh_:
        data = fh_.read()
        result = hashlib.sha512(data).hexdigest()
    return result


def _metadata(filepath):
    """Get exif data.

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

    return result


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
        "--source",
        required=True,
        type=str,
        help="Source directory to process.",
    )
    parser.add_argument(
        "--destination",
        required=True,
        type=str,
        help="Destination of photos with EXIF data.",
    )
    result = parser.parse_args()
    return result


if __name__ == "__main__":
    main()
