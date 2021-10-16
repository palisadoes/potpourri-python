"""Global variables for library."""

from collections import namedtuple

Person = namedtuple('Person', 'firstname lastname email')
Mail = namedtuple('Mail', 'sender receiver subject image body')
MailAuth = namedtuple('MailAuth', 'username password')
