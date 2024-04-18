# ap/scrape_content.py
# Scrape the text content of an Associated Press article.

import requests
from bs4 import BeautifulSoup
import re

def extract_article_text(article_url):
    response = requests.get(article_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    article_body = soup.find('div', class_='RichTextStoryBody')

    if article_body is None:
        return "Article body not found."
    
    text_blocks = []

    for element in article_body.descendants:
        if element.name == 'p':
            # Handle inline elements within the paragraph
            # This is to get around the issue of hyperlinked text being returned
            # without a space before or after it
            paragraph_text = ''
            for child in element.descendants:
                if child.name is None:
                    if child.previous_sibling is not None and child.previous_sibling.name is not None:
                        paragraph_text += ' '
                    paragraph_text += child.strip()
                    if child.next_sibling is not None and child.next_sibling.name is not None:
                        paragraph_text += ' '
            # Remove spaces accidentally inserted before punctuation
            paragraph_text = re.sub(r'\s([.,!?])', r'\1', paragraph_text)
            text_blocks.append(paragraph_text.strip())

    # Honor newline characters (separate paragraphs) by joining the text blocks with two newlines
    return "\n\n".join(text_blocks)

# Example usage
# article_url = "https://apnews.com/article/israel-hamas-war-news-04-02-2024-9bdf66771b62af37d85a2800f71c0e6c"
# article_text = extract_article_text(article_url)
# print(article_text)