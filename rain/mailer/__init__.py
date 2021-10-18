"""Global variables for library."""

from collections import namedtuple

Person = namedtuple('Person', 'firstname lastname email individual validated')
Mail = namedtuple('Mail', 'sender receiver subject image body')
MailAuth = namedtuple('MailAuth', 'username password')
