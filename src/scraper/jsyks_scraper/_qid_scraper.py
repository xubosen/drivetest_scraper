# Scrape question ids from jsyks using requests and BeautifulSoup.

# Library Imports
import requests
from bs4 import BeautifulSoup, SoupStrainer
import json
from typing import List, Dict
import re

# Local Imports
from src.scraper.jsyks_scraper.custom_errors import (JSYKSConnectionError,
                                                     JSYKSContentRetrievalError,
                                                     ConfigError)


class QidScraper:
    """
    Scraper for retrieving question ids from the jsyks site.
    """
    _urls: List[str]
    _div_id: str


    def __init__(self, config_path: str):
        """
        Initialize the QidScraper with a configuration file path.
        """
        with open(config_path, 'r') as file:
            data = json.load(file)
            self._urls = self._load_urls(data)
            self._div_id = data.get('qid_div_id')

    def _load_urls(self, data: Dict) -> List[str]:
        """
        Load URLs from a JSON configuration file.
        """
        base_url = data.get('qid_base_url')
        placeholder = data.get('qid_page_placeholder')
        id_to_page_count = data.get('qid_page_count')
        urls = []
        for page in id_to_page_count.keys():
            page_count = id_to_page_count[page]
            for i in range(1, page_count + 1):
                page_id = f"{page}_{i}"
                url = base_url.replace(placeholder, page_id)
                urls.append(url)
        return urls

    def get_qids(self) -> List[str]:
        """
        Return a list of question ids from the jsyks site.
        :return: List of question ids.
        """
        qid_list = []
        for url in self._urls:
            qid_list.extend(self._extract_qid(self._get_qid_section(url)))
        return qid_list

    def _get_qid_section(self, url: str) -> BeautifulSoup:
        """
        Get the HTML content of a page and return the section containing
        question ids as a BeautifulSoup object.

        :param url: URL of the page to scrape.
        :return: A BeautifulSoup object containing the section with question
        ids.
        """
        response = requests.get(url)
        if 200 <= response.status_code < 300:
            my_filter = SoupStrainer("div", class_ = self._div_id)
            return BeautifulSoup(response.content,
                                 'html.parser',
                                 parse_only=my_filter)
        else:
            raise JSYKSConnectionError(f"Failed to connect to {url}. ")

    def _extract_qid(self, soup: BeautifulSoup) -> List[str]:
        """
        Extract question ids from a BeautifulSoup object.

        :param soup: BeautifulSoup object containing the HTML content.
        :return: List of question ids extracted from the soup.
        """
        qid_list = []
        # Find all <a> tags
        links = soup.find_all('a')

        # Extract question ids from href attributes
        for link in links:
            href = link.get('href')
            if href and '/Post/' in href:
                # Extract the ID part using regex
                match = re.search(r'/Post/([a-zA-Z0-9]+)\.htm', href)
                if match:
                    qid_list.append(match.group(1))
                else:
                    raise JSYKSContentRetrievalError
        return qid_list
