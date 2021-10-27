"""Global variables for library."""

from collections import namedtuple

Person = namedtuple(
    'Person', '''firstname lastname email country state individual validated \
organization''')
Mail = namedtuple('Mail', 'sender receiver subject image body')
MailAuth = namedtuple('MailAuth', 'username password')

CACHE_DIRECTORY = '~/tmp/rain/campaigns'
