"""Application module to manage html in email."""

# Standard imports
from bs4 import BeautifulSoup


class File():
    """Class to manipulate HTML file data."""

    def __init__(self, html):
        """Initialize the class.

        Args:
            html: HTML code

        Returns:
            None

        """
        # Initialize key variables
        self._soup = BeautifulSoup(html, features='lxml')
        for tag in self._soup():
            for attribute in ['class', 'id', 'name', 'style']:
                del tag[attribute]

    def body(self):
        """Get body from HTML.

        Args:
            None

        Returns:
            result: Body HTML

        """
        # Return result
        items = []
        body = self._soup.find('body')

        for item_ in body.findChildren(recursive=False):
            # Replace carriage returns with spaces
            item = ' '.join(str(item_).split('\n'))

            # Remove duplicate white space
            item = ' '.join(item.split())

            # Remove white space after brackets
            item = item.replace('> ', '>')
            items.append(item)

        # Strip </br> and return
        result = ''.join(items).replace('<p><br/></p>', '')
        return result
