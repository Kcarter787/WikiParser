from urllib.request import urlopen
from urllib import parse
import time
import bs4
from is_italics import is_italics, find_external_stylesheets
"""
I recognized that Wikipedia only uses external style sheets and thus
built two options for retrieving the font-style. The implemented method
looks directly inside the external style sheets and returns True if the
class or its parent has a italic font-style. In italics.py, an alternate
method (find_non_italic_link) uses a chrome driver to get the computed
font-style. The chrome driver has the benefit of accuracy when compared to
parsing the complex stylesheets that wikipedia uses. However, because of the
significant difference in speed (over hundreds of requests), I opted to go with
parsing anyway. I left the code for the driver in case there is interest.

Improvements:
Cache the wiki html class names with their corresponding is_italics boolean

"""

# IntraPage parser handles the internal actions required on a single wiki page
class _WikiIntraPageParser():

    def __init__(self, wiki_page_html):
        super(_WikiIntraPageParser, self).__init__()
        self._base_url = "https://en.wikipedia.org"
        self._page_html = wiki_page_html
        self._links = self.find_page_links(wiki_page_html)
        self.style_urls = find_external_stylesheets(wiki_page_html)
        self._first_valid_link = self.find_first_link()

    # Find all click-able links
    def find_page_links(self, html_string):
        """Returns list of all href strings within html_string"""
        soup = bs4.BeautifulSoup(html_string, "html.parser")
        links = []
        for link in soup.find_all("a", attrs={"href": True}):
            if self.is_desired_href(link['href']):
                links.append(link)
        return links

    # Find the first one not in parenthesis or italicized
    def find_first_link(self):
        """Returns the first link not in parenthesis or italicized"""
        for link in self._links:
            if not self._is_within_parenthesis(link['href']) and not \
                    self._is_italics(
                        link):
                return self.make_url(self._base_url, link['href'])

    def _is_within_parenthesis(self, link):
        """
        Returns true if the href is encapsulated by parenthesis in its
        left and right strings, regardless of validity
        """
        before_string, after_string = self._page_html.split(link, maxsplit=1)
        return self._has_open_parenthesis(before_string) and \
               self._has_closed_parenthesis(after_string)

    @property
    def first_valid_link(self):
        return self._first_valid_link

    @staticmethod
    def is_desired_href(href):
        """Returns true if href does not contain the following strings"""
        undesired_links = ["#", "index.php?", ":"]
        valid_link = True
        for x in undesired_links:
            if x in href:
                valid_link = False
        return valid_link

    @staticmethod  # A helper for forming valid URLs
    def make_url(base, link):
        """Returns a joined url, throws an error if base is missing in result"""
        url = parse.urljoin(base, link)
        if base not in url:
            raise NoValidLinkError \
                ("{}{} redirects to a non wikipedia page".format(base, link))
        else:
            return url

    @staticmethod
    def _has_open_parenthesis(string):
        """
        Returns true if the string encapsulates its right side--
        regardless of validity, i.e) "((()"-> True
        """
        parenthesis_count = 0
        reversed_string = reversed(string)
        for char in reversed_string:
            if char == "(":
                parenthesis_count += 1
            elif char == ")":
                parenthesis_count -= 1
            if parenthesis_count >= 1:
                return True
        return False

    @staticmethod
    def _has_closed_parenthesis(string):
        """
        Returns true if the string encapsulates its left side
        regardless of validity, i.e) "))()"-> True
        """
        parenthesis_count = 0
        for char in string:
            if char == "(":
                parenthesis_count += 1
            elif char == ")":
                parenthesis_count -= 1
            if parenthesis_count <= -1:
                return True
        return False

    def _is_italics(self, link):
        """
        Returns true if link or link's parent has font-style: italic.
        For alternative, use find_non_italic link from is_italics.py for
        computed italics attribute
        """
        is_italic = False
        # Find the class name
        if link.has_attr('class'):
            class_name = link['class'][0]
            is_italic = is_italics(class_name, self.style_urls)
            if not is_italic:
                parents = link.find_parents(attrs={"class": True}, limit=1)
                if parents:
                    is_italic = is_italics(parents[0]['class'], self.style_urls)
        return is_italic

# InterPage parser handles the wiki page hierarchy from start to finish
class WikiInterPageCrawler():
    def __init__(self, wiki_source_url, confirmed_path_data={}):
        super(WikiInterPageCrawler, self).__init__()
        self._base_url = "https://en.wikipedia.org/wiki/"
        self._current_url = wiki_source_url
        self._pages_crawled = 0
        self._pages_cache = {}
        self._page_html = None
        self.fetch_html()
        self.confirmed_path_data = confirmed_path_data

    def __iter__(self):
        return self

    # Find the next valid link from the current page
    def __next__(self):
        self.fetch_html()
        next_url = self.find_next_url()
        # Keep track of the pages we've encountered
        self._pages_cache[self.current_url] = self._pages_crawled
        self.crawl_to(next_url, self._pages_cache)

    def find_next_url(self):
        """Returns the first valid url on the page"""
        try:
            wiki_parser = _WikiIntraPageParser(self.page_html)
            next_url = wiki_parser.first_valid_link
            return next_url
        except NoValidLinkError as e:
            # Ignore values that don't meet our criteria
            self.reset_data()

    # Set the specified url and increment page count by 1,
    # handle loops and dead-ends by reseting everything
    def crawl_to(self, url, cache):
        """Calls update_state, handles errors by resetting"""
        try:
            self.update_state(url, cache=cache)
        except LoopError as e:
            # Re-encountered a page
            # e.report_skipped_link()
            self.reset_data()
        except NoValidLinkError as e:
            # No link meets our criteria
            # e.report_skipped_link()
            self.reset_data()

    # Point out occurrences of loops and dead ends
    # Update state if they are absent
    def update_state(self, url, cache):
        """
        Increments self.current_url and self._pages_crawled when
        conditions are met
        """
        if url:
            if url not in cache:
                self.current_url = url
                self._pages_crawled += 1
            else:
                raise LoopError \
                        ("The interpage crawler re-encountered url: {} before "
                        "reaching its destination".format(url))
        else:
            raise NoValidLinkError\
                ("Current URL: {} has no link to crawl to that meets "
                 "our criteria.".format(self.current_url))

    # Get the html from the current url
    def fetch_html(self):
        """Assigns to self.page_html from response generated by
        self.current_url"""
        response = urlopen(self.current_url)
        if response.getheader(
                'Content-Type') == 'text/html' or response.getheader(
            'Content-Type') == "text/html; charset=UTF-8":
            htmlBytes = response.read()
            htmlString = htmlBytes.decode("utf-8")
            self.page_html = htmlString
        else:
            raise ValueError \
                    ("Url {} has incorrect content-type: {}.\n Must "
                     "be text/html".format(response.getheader(
                    'Content-Type'), self.current_url))

    # Compute the results of the fully completed crawl
    def compute_path_info(self):
        """Returns a dictionary of url: distance to current page"""
        pages, count = self.pages_cache, self.pages_crawled
        path_info = {page: count - idx for page, idx in pages.items()}
        return path_info

    # Re-init with a random url if needed
    def reset_data(self,
                   new_start_url="https://en.wikipedia.org/wiki/Special"
                                 ":Random"):
        self.__init__(new_start_url)

    @property
    def page_html(self):
        return self._page_html

    @page_html.setter
    def page_html(self, value):
        # We only need the main content html
        self._page_html = value[value.find('<p>'):]

    @property
    def current_url(self):
        return self._current_url

    @current_url.setter
    def current_url(self, value):
        if self._base_url not in value:
            raise ValueError
        ("Input URL: {} is missing the base url: {}".format(value,
                                                            self._base_url))
        self._current_url = value

    @property
    def pages_cache(self):
        return self._pages_cache

    @property
    def pages_crawled(self):
        return self._pages_crawled


class LoopError(Exception):
    def __init__(self, message):
        super(LoopError, self).__init__(message)
        self.message = message

    def report_skipped_link(self):
        print("Skipping link because {}\n".format(self.message))


class NoValidLinkError(Exception):
    def __init__(self, message):
        super(NoValidLinkError, self).__init__(message)
        self.message = message

    def report_skipped_link(self):
        print("Skipping link because {}\n".format(self.message))


if __name__ == "__main__":

    def timing_function(function):
        """
        Outputs the time a function takes
        to execute.
        """

        def wrapper(self):
            t1 = time.time()
            function(self)
            t2 = time.time()
            return "Time it took to run the function: " + str((t2 - t1)) + "\n"
        return wrapper

