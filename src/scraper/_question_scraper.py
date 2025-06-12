# Scrape question content, multiple choice options, and answers using requests
# and BeautifulSoup.

# Library Imports
import requests
from bs4 import BeautifulSoup
from typing import List

# Module Imports
from configurations.site_info import SiteInfo
from scraper.question import Question, FourChoiceText, TwoChoiceText

class QuestionScraper:
    """
    Scraper that retrieves the content of a question.
    """
    _site_info: SiteInfo

    def __init__(self, site_info: SiteInfo):
        """
        Initializes the QuestionScraper with the provided site information.
        """
        self._site_info = site_info

    def get_content(self, q_id: str) -> Question:
        raise NotImplementedError
