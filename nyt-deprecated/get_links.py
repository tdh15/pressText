# nyt/get_links.py
# Use NYT API to get links and other info for today's articles

# Reference: https://developer.nytimes.com/docs/top-stories-product

# This NYT API call works, but I couldn't get the scraper working, so we gotta
# leave it alone.

import requests
import os
nyt_api_key = os.environ.get('NYT_API_KEY')

# Output:
# data (dictionary): main data structure used to store the processed articles.
#   - Keys: categories ('us', 'world', 'business', 'arts')
#   - Values: list of of dictionaries, each representing an article. The article dictionary key-value pairs are:
#       - (key: value)
#       - title: the title of the article (string)
#       - abstract: abstract of the article (string)
#       - url: URL to the full article on the NYT website (string)
#       - published_date: date when the article was published (string)

# Define a function to fetch and process data from the NYT API
# Defaults to getting 5 articles from each category
def fetch_nyt_data(categories, articles_per_category=5):
    base_url = "https://api.nytimes.com/svc/topstories/v2/{}.json?api-key={}"
    data = {}

    for category in categories:
        response = requests.get(base_url.format(category, nyt_api_key))
        if response.status_code == 200:
            articles = response.json().get("results", [])[:articles_per_category]
            data[category] = [
                {
                    "title": article["title"],
                    "abstract": article["abstract"],
                    "url": article["url"],
                    "published_date": article["published_date"],
                    "byline": article["byline"] if "byline" in article else ""
                }
                for article in articles
            ]
        else:
            print(f'Failed to fetch {category} data.')
            print(f'{response.status_code}: {response.text}')
            data[category] = []

    return data

# For testing/demonstration:
# 
# categories = ['us', 'world', 'business', 'arts']
# 
# # Fetch and process the data
# nyt_data = fetch_nyt_data(categories)
# 
# # Print the processed data
# for category, articles in nyt_data.items():
#    print(f"Category: {category}")
#    for article in articles:
#        print(article)
#    print("\n")
