# ap/get_links.py
# Go to the Associated Press frontpage for a category and grab the links to the articles.

import requests
from bs4 import BeautifulSoup

# Outputs dictionary of the form {title: link, title: link, ...}
def get_links(frontpage_url):
    print("Getting links from:", frontpage_url)
    response = requests.get(frontpage_url)

    # Create a BeautifulSoup object to parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the div containing the featured articles
    featured_articles_div = soup.find("div", class_="PageList-items")

    # Find all the article divs within the featured articles div
    article_divs = featured_articles_div.find_all("div", class_="PagePromo")

    print("Found", len(article_divs), "articles.\n")

    # Output dictionary of the form {title: link}
    articles = {}

    # Iterate over the article divs and extract the titles and links
    for article_div in article_divs:
        # Find the title element and extract its text
        title_element = article_div.find("h3", class_="PagePromo-title")
        title = title_element.text.strip()

        # Find the link element and extract its href attribute
        link_element = title_element.find("a")
        link = link_element["href"]

        # Add the title and link to the dictionary
        articles[title] = link

    return articles

# Example usage
# url = "https://apnews.com/entertainment"
# articles = get_links(url)
# print(articles)