"""Global variables for library."""

from collections import namedtuple

Person = namedtuple(
    'Person', 'firstname lastname email country state individual validated')
Mail = namedtuple('Mail', 'sender receiver subject image body')
MailAuth = namedtuple('MailAuth', 'username password')
