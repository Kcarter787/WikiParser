from numpy import polyfit, poly1d
import matplotlib.pyplot as plt


def plot_data(path_lengths, requests_made, url_count):
    """
    Displays a scatter plot showing the path length and # of requests for each
    starting url
    """
    plt.figure(figsize=(20, 8))
    _draw_plots(path_lengths, requests_made, url_count)
    plt.title("Path length for {} links".format(url_count), size="16")
    plt.xlabel("Link number")
    plt.ylabel("Path Length")
    plt.xlim(- 5, url_count + 5)
    plt.legend(loc="upper right")
    plt.show()

def _draw_plots(path_lengths, requests_made, url_count):
    """Draws the plots, catches input error when sizes unequal"""
    try:
        x_points = [num for num in range(1, url_count + 1)]
        _plot_path_lengths(x_points, path_lengths)
        _plot_requests_made(x_points, requests_made)
    except ValueError:
        print(
            "ERROR: Plot could not be created. plot_data parameters must all "
            "have the same size")

def _plot_path_lengths(x_points, path_lengths):
    """Plots from a list of path lengths"""
    # Plot the path length of each start-point link
    plt.scatter(x_points, path_lengths,
                marker="o",
                color="b",
                alpha=0.7,
                s=50,
                label="Path Length")

def _plot_requests_made(x_points, requests):
    """Plots the number of requests made per start-point link"""
    # Plot the http requests made
    plt.scatter(x_points, requests,
                marker="x",
                color='r',
                alpha=0.7,
                s=50,
                label="Http Requests")
    # Linear fit (to observe decrease in requests)
    fit = polyfit(x_points, requests, 1)
    fit_fn = poly1d(fit)
    plt.plot(x_points, requests, 'bo', x_points, fit_fn(x_points), '-r',
             marker=False,
             color='r',
             alpha=0.7,
             linewidth=1,
             markersize=0)


if __name__ == "__main__":
    # Test plots here
    path_lengths = [12, 18, 4, 22, 8, 19, 14, 16, 12, 19]
    requests = [num - 3 for num in path_lengths]
    plot_data(path_lengths, requests, 10)
