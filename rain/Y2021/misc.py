"""Miscellaneous Functions."""

from __future__ import print_function
import time
import datetime


def timestamp(datestring):
    """Convert RFC3339 datestring to timestamp.

    Args:
        datestring: RFC3339 date string

    Returns:
        result: timestamp

    """
    # Return
    newstring = '{}T'.format(datestring).upper()
    date = newstring.split('T')[0]
    result = time.mktime(
        datetime.datetime.strptime(date, '%Y-%m-%d').timetuple())
    return result
