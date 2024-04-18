# ap/get_ap_data.py
# Get the content of the AP articles for the day (using the other helper functions)

from ap.get_links import get_links
from ap.scrape_content import extract_article_text

# Outputs dictionary of the form:
# {
#   category: { article_url: [title, article_text], article_url: [title, article_text], ...},
#   category: { article_url: [title, article_text], article_url: [title, article_text], ...},
#   ...
# }

def get_ap_data():
    print("Getting the content of the AP articles for the day.\n")

    ap_data = {}

    # Categories and their URL suffixes (for the frontpage URL for that section)
    categories = {"us": "us-news", "world": "world-news", "business": "business", "arts": "entertainment"}

    for category, category_url_suffix in categories.items():
        print(f"Getting AP data from category: {category}")
        ap_data[category] = {}
        frontpage_url = f"https://apnews.com/{category_url_suffix}"

        articles = get_links(frontpage_url)
        for title, article_url in articles.items():
            article_text = extract_article_text(article_url)
            
            # Store the article information under the appropriate category in ap_data
            ap_data[category][article_url] = [title, article_text]

    return ap_data