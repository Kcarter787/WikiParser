from urllib.request import urlopen
from urllib import parse
import requests
import bs4
from selenium import webdriver
import os

"""--CHROME DRIVER EXE FILE--"""
# http://chromedriver.storage.googleapis.com/index.html

EXE_PATH = "/Users/kevincarter/Downloads/chromedriver"
BASE_URL = "https://en.wikipedia.org"

# Use this if accuracy is more important than speed (~3x slower than urlopen)
def find_non_italic_link(url, links):
    """Returns the first non-italic link on the page, else empty str"""
    # Driver Setup
    chromedriver = EXE_PATH
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chromedriver)
    driver.get(url)
    non_italic_link = ""
    # Find the 1st link with a non-italic computed font-style
    for link in links:
        attr_link = driver.find_element_by_css_selector("a[href={}]".format(
            link))
        if "italic" not in attr_link.value_of_css_property("font-style"):
            non_italic_link = link
            break
    driver.quit()
    return non_italic_link

# Get urls for all external sheets
def find_external_stylesheets(html_string):
    """Returns a list of urls to the page's external stylesheets"""
    soup = bs4.BeautifulSoup("<html>{}</html>".format(html_string),
                             "html.parser")
    ext_styles = soup.find_all('link', rel="stylesheet")
    links = []
    for style in ext_styles:
        if style.has_attr("href"):
            link = style.attrs["href"]
            links.append(parse.urljoin(BASE_URL, link))
    return links

def find_italic_attr(class_name, css_text):
    """Returns True if class_name has 'italic' within its content"""
    start = 0
    finish = 0
    # Look for italics within every mention of the class content
    while start != -1:
        start = css_text.find(class_name + "{", finish)
        finish = css_text.find("}", start)
        if "italic" in css_text[start: finish]:
            return True
    return False

def is_italics(class_name, style_urls):
    """Returns True if the class's content has 'italics' in its external
    stylesheet"""
    for link in style_urls:
        res = requests.get(link)
        css_text = res.text
        if find_italic_attr(class_name, css_text):
            return True
    return False

if __name__ == "__main__":
    # Test italics helpers here:

    def fetch_html(url):
        response = urlopen(url)
        if response.getheader(
                'Content-Type') == 'text/html' or response.getheader(
            'Content-Type') == "text/html; charset=UTF-8":
            htmlBytes = response.read()
            htmlString = htmlBytes.decode("utf-8")
            return htmlString
        else:
            raise ValueError \
                    (
                    "Url {} has incorrect content-type: {}.\n Must be "
                    "text/html".format(
                        response.getheader('Content-Type'), url))

    def test_soup(html):
        soup = bs4.BeautifulSoup(html, "html.parser")
        is_italic = False
        # Wiki only uses external font styling, thus find the class name
        tester = soup.find("a",
                           attrs={"href": "/wiki/Science_(disambiguation)"})
        soup = bs4.BeautifulSoup(html_string, "html.parser")
        links = []
        for link in soup.find_all("a", attrs={"href": True}):
            print(link["href"])

    html_string = fetch_html("https://en.wikipedia.org/wiki/Science")
    test_soup(html_string)


