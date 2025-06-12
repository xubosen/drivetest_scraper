# Library Imports
import pytest
from bs4 import BeautifulSoup

# Module Imports
from scraper.question import Question
from scraper.jsyks_scraper._question_scraper import QuestionScraper

QUESTION_IDS = ["c6219", "d150f", "ad9e0", "b5211", "cd86b"]
IMG_PATH = "db_test/img"
CONFIG_PATH = "scraper_test/site_info.json"

def test_format_url():
    """
    Test the URL formatting function.
    """
    scraper = QuestionScraper(IMG_PATH, CONFIG_PATH)
    q_id = "12345"
    expected_url = "https://tiba.jsyks.com/Post/12345.htm"
    assert scraper._format_url(q_id) == expected_url, "URL formatting failed."

def test_get_webpage():
    """
    Test the webpage fetching function.
    """
    scraper = QuestionScraper(IMG_PATH, CONFIG_PATH)
    url = scraper._format_url("c6219")
    soup = scraper._get_webpage(url)
    # Print the soup for debugging purposes
    print(soup.prettify())
