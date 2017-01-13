from urllib import error
from crawler_objects import WikiInterPageCrawler
from stats import plot_data

# Setup components
RANDOM_URL_COUNT = 10  # Number of random urls to compute the path length for
END_URL = "https://en.wikipedia.org/wiki/Philosophy"
global_path_cache = {END_URL: 0}

def generate_random_wiki_link():
    return "https://en.wikipedia.org/wiki/Special:Random"

def set_up_wiki_crawler(link):
    """
    Returns a new instance of a wiki inter-page crawler. Prints possible errors
    """
    try:
        crawler = WikiInterPageCrawler(link)
        return crawler
    except TimeoutError:
        print("\nTimeout Error from bad link: {}\n".format(link))
    except error.HTTPError:
        print(error.HTTPError.msg)

# Catch obscure errors caused when reading the html on some wiki pages
def reroll_bad_values(function):
    """Resets a crawler if value error"""
    def wrap_errors(crawler, end_url):
        try:
            res = function(crawler, end_url)
            return res
        except ValueError:
            print("REROLLING A VALUE")
            crawler.reset_data()
            function(crawler, end_url)
    return wrap_errors

def update_global_cache(crawler):
    """Mutates global_path_cache"""
    global global_path_cache
    info = crawler.compute_path_info()
    global_path_cache.update(info)

@reroll_bad_values
def crawl_to_wiki_page(crawler, end_url):
    """
    Iterates through a crawler until it reaches its destination. Relies on
    the crawler properly re-initing itself if needed.
    """
    for page in crawler:
        if crawler.current_url == end_url:
            # Found Philosophy page
            path_length = crawler.pages_crawled
            # To reduce num of future http requests...
            update_global_cache(crawler)
            return path_length
        elif crawler.current_url in global_path_cache:
            path_length = crawler.pages_crawled + global_path_cache[
                crawler.current_url]
            # Account for alternate paths to the same page
            update_global_cache(crawler)
            return path_length
        else:
            # Keep going until we hit the end or a loop
            pass

def report_one_result(i, path_length, http_requests_made,
                      http_requests_avoided):
    """Prints some useful info to look at while parsing"""
    print(
        "Link #{} has a path length of {} pages to the philosophy "
        "page".format(
            i + 1, path_length))
    print("HTTP REQUESTS MADE: {}".format(http_requests_made))
    print("HTTP REQUESTS Avoided: {}\n".format(http_requests_avoided))

def report_totals(total_made, total_avoided):
    """Prints the end result totals.
    *these totals don't include requests to external stylesheets (which could
    be reduced in the same way with additional caching).
    """
    # 0.2 sec comes from timing fetch_html() in crawler_objects.py
    print("\n TOTAL HTTP REQUESTS MADE: {}, Approx {:.3g} seconds".format(
        total_made, total_made * 0.2))
    print("\n TOTAL HTTP REQUESTS AVOIDED: {}, Approx {:.3g} "
          "seconds".format(total_avoided, total_avoided * 0.2))
    print("\n Efficiency boost = {0:.3g}%".format((total_avoided / total_made)
                                                  * 100))

def main():
    """Plots the path length of 500 random starting points"""
    # Init the values we wish to compute
    path_lengths, http_requests_made, http_requests_avoided = [], [], []
    # Crawl to the philosophy page for each starting link
    for i in range(RANDOM_URL_COUNT):
        link = generate_random_wiki_link()
        crawler = set_up_wiki_crawler(link)
        path_length = crawl_to_wiki_page(crawler, END_URL)

        # Track the result
        path_lengths.append(path_length)
        http_requests_made.append(crawler.pages_crawled)
        http_requests_avoided.append(global_path_cache[crawler.current_url])

        # Print the single result
        report_one_result(i, path_length, http_requests_made,
                          http_requests_avoided)

    # Compute some fun stats
    total_made, total_avoided = sum(http_requests_made), \
                                sum(http_requests_avoided)
    # Report all the stats
    report_totals(total_made, total_avoided)

    # Plot all the data
    plot_data(path_lengths, http_requests_made, RANDOM_URL_COUNT)

main()