import json
from lxml import html
import requests
from time import sleep
from urlparse import urljoin


DELAY_TIME = 2
MSG = {
    '0': "ALERT - Can't move to page {}: page {} link has been malevolently \
tampered with!!",
    '1': "Move to page {}",
}


class PetitPoucet(object):
    """Web scraper with an easily extendable data model for web pages.

    The starting point will always have "0" as the key and url as the first
    link to be queried.
    """
    def __init__(self, url):
        self._input_file = open("thumbscraper_input_tampered.json", "r+")
        self._input = json.loads(self._input_file.read())
        self._count_pages = 1
        self._item = self._input.get("0")
        self._url = url

    def make_request(self):
        """Performs request and builds lxml tree from it."""
        page = requests.get(self._url)
        tree = html.fromstring(page.content)

        return tree

    def extract_url(self, tree):
        """Extracts url from the tree xpath, if the url doesn't match the
        given path we assume it has been tampered with."""
        href = tree.xpath(self._item.get("xpath_button_to_click"))
        if not href:
            raise IndexError
        url = dict(href[0].items()).get('href')

        return urljoin(url_start, url)

    def parse_response(self, tree):
        """Matches the test query against the result from the web page and in
        case this fails we assume the page has been tampered with."""
        result = tree.xpath(self._item.get("xpath_test_query"))
        if not self.match(result):
            raise ValueError
        self._url = self.extract_url(tree)

    def match(self, result):
        """Check if all the values in the result match the expected one."""
        return all(map(lambda r: r in self._item.get("xpath_test_result"),
                       result))

    def next(self):
        """Moves crawler to the next expected page."""
        self._item = self._input.get(self._item.get("next_page_expected"))

    def delay(self):
        """Respect webcrawling ethics delaying requests on the server."""
        sleep(DELAY_TIME)

    def log(self, move='1'):
        """Logs progress to output."""
        print(MSG.get(move).format(self._count_pages,
                                   self._count_pages - 1))

    def run(self):
        """Runs the web crawler."""
        while True:
            try:
                self.log()
                tree = self.make_request()
                self._count_pages += 1
                self.parse_response(tree)
                self.next()
                self.delay()
            except Exception:
                self.log('0')
                break


if __name__ == "__main__":
    url_start = "https://www.legalstart.fr"
    petit = PetitPoucet(url_start)
    petit.run()
