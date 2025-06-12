# Scrape question content, multiple choice options, and answers using requests
# and BeautifulSoup.

# Library Imports
import requests
from bs4 import BeautifulSoup
import json

# Module Import
from scraper.question import Question


class QuestionScraper:
    """
    Scraper that retrieves the content of a question.
    """
    _img_dir: str
    _config_path: str
    _generic_url: str
    _url_placeholder: str
    _qid: str

    def __init__(self, img_dir: str, config_path: str):
        """
        Initializes the QuestionScraper with the site information in the json
        file.
        """
        self._img_dir = img_dir
        self._config_path = config_path
        self._generic_url = ""
        self._get_site_info()

    def _get_site_info(self):
        """ Load the site information from the site_info.json file. """
        with open(self._config_path, "r") as file:
            site_info = json.load(file)
            self._generic_url = site_info["url"]
            self._url_placeholder = site_info["url_placeholder"]

    def _format_url(self, q_id: str) -> str:
        """
        Return the correct url to request for by replacing the placeholder with
        the question ID.
        :param q_id:
        :return:
        """
        return self._generic_url.replace(self._url_placeholder, q_id)

    def _get_webpage(self, url: str) -> BeautifulSoup:
        """
        Fetches the webpage content from the given URL.
        :param url: The URL of the webpage to scrape.
        :return: BeautifulSoup object containing the parsed HTML content.
        """
        response = requests.get(url)
        if 200 <= response.status_code < 300: # Successful response
            return BeautifulSoup(response.content,'html.parser')
        else:
            raise JSYKSConnectionError(f"Failed to connect to {url}. "
                                       f"Status code: {response.status_code}")

    def get_content(self, q_id: str) -> Question:
        """
        Retrieves the content of a question by its ID.
        :param q_id:
        :return: The Question object containing the question content, options,
        image, and answer.
        """
        url = self._format_url(q_id)
        webpage = self._get_webpage(url)


        raise NotImplementedError


class JSYKSConnectionError(ConnectionError):
    """
    Custom exception for connection errors in the JSYKS scraper.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class ContentNotFoundException(Exception):
    """
    Custom exception for when content is not found in the JSYKS scraper.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
