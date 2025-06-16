# Scrape question ids from jsyks using requests and BeautifulSoup.

# Library Imports
import requests
from bs4 import BeautifulSoup, SoupStrainer
import json
from typing import List, Dict, Set
from logging import Logger
import re

# Local Imports
from scraper.jsyks_scraper.custom_errors import (JSYKSConnectionError,
                                                 JSYKSContentRetrievalError)


class QidScraper:
    """
    Scraper for retrieving question ids from the jsyks site.
    """
    _logger: Logger
    _clst_cid: str
    _pb_cid: str
    _qlst_cid: str
    _base_url: str
    _chapters: Dict[int, str]
    _chapt_to_chapturl: Dict[int, str]
    _chapt_to_urls: Dict[int, List[str]]
    _connected: bool

    def __init__(self, logger: Logger, config_path: str):
        """
        Initialize the QidScraper with a configuration file path.

        :param logger: Logger instance for logging the scraping process
        :param config_path: Path to the JSON configuration file containing site
        information
        """

        # Initialize empty attributes
        logger.info("Initializing QidScraper...")
        self._logger = logger
        self._chapters = {}
        self._chapt_to_urls = {}

        # Load configuration from the provided JSON file
        self._logger.info("Loading configuration file...")
        with open(config_path, "r") as file:
            config = json.load(file)
        self._clst_cid = config.get("c_lst_cls_name")
        self._pb_cid = config.get("page_bar_cls_name")
        self._qlst_cid = config.get("q_lst_cls_name")
        self._base_url = config.get("base_url")

        # Initialize remaining private attributes with empty dictionaries
        self._chapters = {}
        self._chapt_to_chapturl = {}
        self._chapt_to_urls = {}

        self._connected = False

    def connect(self):
        """
        Connect to the jsyks site and retrieve chapter information.
        :return:
        """
        # Scrape chapters from the base url
        self._logger.info(f"Retrieving chapters from {self._base_url}")
        section = self._extract_chapter_section(self._base_url)

        self._logger.info("Extracting chapter information")
        self._extract_chapters(section)

        self._logger.info("Setting up chapter to URLs mapping...")
        self._set_up_urls()
        self._logger.info("Chapter information retrieved.")
        self._connected = True

    def _extract_chapter_section(self, url: str) -> BeautifulSoup:
        """
        Extract the chapter section from the provided URL.

        :param url: URL of the page to scrape
        :return: BeautifulSoup object containing the chapter section
        :raises JSYKSConnectionError: If connection to the URL fails
        """
        html_page = requests.get(url)
        try:
            my_filter = SoupStrainer("div", class_=self._clst_cid)
            return BeautifulSoup(html_page.content,
                                 'html.parser',
                                 parse_only=my_filter)
        except ConnectionError:
            raise JSYKSConnectionError(f"Failed to connect to {url}. "
                                       f"Status code: {html_page.status_code}")

    def _extract_chapters(self, section: BeautifulSoup):
        """
        Extract chapter information from the chapter section.

        :param section: BeautifulSoup object containing the chapter section
        """
        # Get all the <li> tags
        list_item = section.find_all('li')

        # Look inside the "a" tag within each li tag
        for li in list_item:
            a = li.find('a')
            # Look inside the tag to find the chapter name
            self._logger.debug(f"Looking for chapter name in {a.get_text()}")
            # Make sure to use chinese “：”
            index, descr = a.get_text().split("：")

            # Convert index to integer (第1章 -> 1)
            chapter_num = int(re.search(r'第(\d+)章', index).group(1))

            # Store the chapter number and description in the dictionary
            self._chapters[chapter_num] = descr.strip()

            # Get the chapter link url from the href attribute and store it
            self._chapt_to_chapturl[chapter_num] = a.get('href')

    def _set_up_urls(self):
        """
        Set up URLs for all chapters by retrieving pagination information.

        :raises JSYKSConnectionError: If connection to any chapter URL fails
        """
        for chapter in self._chapters.keys():
            self._logger.info(f"Setting up URLs for chapter {chapter}...")
            self._chapt_to_urls[chapter] = []
            page = requests.get(self._chapt_to_chapturl[chapter])
            if 200 <= page.status_code < 300:
                my_filter = SoupStrainer("div", class_=self._pb_cid)
                page_bar = BeautifulSoup(page.content,
                                         'html.parser',
                                         parse_only=my_filter)
                self._extract_urls(page_bar, chapter)
            else:
                raise JSYKSConnectionError(f"Failed to connect to "
                                           f"{self._chapt_to_chapturl[chapter]}"
                                           f". Status code: {page.status_code}")

    def _extract_urls(self, page_bar: BeautifulSoup, chapter: int):
        """
        Extract all page URLs for a specific chapter given the BeautifulSoup
        object containing the choose-your-page bar.

        :param page_bar: BeautifulSoup object containing the page bar
        :param chapter: Chapter number for which to extract URLs
        """
        # Look for the <a> tag with the string "尾页"
        last_page_button = page_bar.find('a', string='尾页')
        # If there is a last page button, check the href attribute of its url
        if last_page_button:
            last_page_url = last_page_button.get('href')
        # If not, find the url of the last page displayed
        else:
            a_s = page_bar.find_all('a')
            # The last a tag is for "next page"
            last_page_url = a_s[-2].get('href')

        # Parse url
        _, chapter_code, page_count = tuple(last_page_url.split('_'))

        # Generate URLs for all pages in the chapter
        for i in range(1, int(page_count) + 1):
            # Construct the URL for each page
            self._chapt_to_urls[chapter].append(
                f"{self._base_url}_{chapter_code}_{i}")

    def get_chapters(self) -> Dict[int, str]:
        """
        Return a dictionary of chapter numbers and their names.

        :return: Dictionary mapping chapter numbers to chapter names
        """
        if not self._connected:
            raise JSYKSContentRetrievalError("Not connected to jsyks site. "
                                             "Call connect() first.")
        return self._chapters

    def get_chapter_to_qids(self) -> Dict[int, Set[str]]:
        """
        Retrieve all question IDs for each chapter.

        :return: Dictionary mapping chapter numbers to sets of question IDs
        """
        if not self._connected:
            raise JSYKSContentRetrievalError("Not connected to jsyks site. "
                                             "Call connect() first.")
        chapt_to_qids = {}
        for chapter in self._chapters.keys():
            chapt_to_qids[chapter] = set()
            for url in self._chapt_to_urls[chapter]:
                self._logger.info(f"Retrieving question ids from {url}")
                section = self._get_qid_section(url)
                chapt_to_qids[chapter].update(self._extract_qid(section))
        return chapt_to_qids

    def _get_qid_section(self, url: str) -> BeautifulSoup:
        """
        Get the HTML section containing question IDs from the specified URL.

        :param url: URL of the page to scrape
        :return: BeautifulSoup object containing the question ID section
        :raises JSYKSConnectionError: If connection to the URL fails
        """
        response = requests.get(url)
        if 200 <= response.status_code < 300:
            my_filter = SoupStrainer("div", class_=self._qlst_cid)
            return BeautifulSoup(response.content,
                                 'html.parser',
                                 parse_only=my_filter)
        else:
            raise JSYKSConnectionError(f"Failed to connect to {url}. ")

    def _extract_qid(self, sec: BeautifulSoup) -> Set[str]:
        """
        Extract question IDs from a BeautifulSoup object containing question
        links.

        :param sec: BeautifulSoup object containing the section with question
        links
        :return: Set of question IDs extracted from the links
        """
        qids = set()
        # Find all <a> tags
        a_tags = sec.find_all('a')
        for a_tag in a_tags:
            # Extract the url from the href attribute
            url = a_tag.get('href')
            # Extract the question id ("/Post/c122c.htm" -> "c122c")
            qids.add(url.split('/')[2].split('.')[0])
        return qids
