# Scrape question content, multiple choice options, and answers using requests
# and BeautifulSoup.

# Library Imports
import requests
from bs4 import BeautifulSoup, SoupStrainer
import json
from typing import Set, List
import os.path

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
    _questn_div_id: str
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
            self._questn_div_id = site_info["div_id"]

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
        parse_filter = SoupStrainer(id=self._questn_div_id)
        if 200 <= response.status_code < 300: # Successful response
            return BeautifulSoup(response.content,
                                 'html.parser',
                                 parse_only=parse_filter)
        else:
            raise JSYKSConnectionError(f"Failed to connect to {url}. "
                                       f"Status code: {response.status_code}")

    def _extract_question(self, qid: str, soup: BeautifulSoup) -> Question:
        """
        Extract the question from the HTML soup based on format specified in
        site_info.json.

        :param qid: The question ID.
        :param soup:
        :return Question: The Question object containing the question content,
        """
        header = soup.find("h1")
        answers, ans = self._extract_answers(header)

        img_url = self._extract_img_url(header)
        if img_url is not None:
            img_path = self._download_img(qid, img_url, self._img_dir)
        else:
            img_path = None

        return Question(
            qid=qid,
            question=self._extract_question_text(header),
            answers=answers,
            correct_answer=ans,
            img_path=img_path
        )

    def _extract_question_text(self, h1) -> str:
        strong = h1.find("strong")
        a = strong.find("a")
        return a.get_text(strip=True)

    def _extract_img_url(self, h1) -> str | None:
        img = h1.find("img")
        if (img is not None) and img.has_attr("src"):
            return img["src"]
        else:
            return None

    def _download_img(self, qid:str, img_url: str, save_path: str) -> str:
        """
        Download the image from the given URL and save it to the specified
        path.

        :param qid: The question ID, used to create a unique filename.
        :param img_url: The URL of the image to download.
        :param save_path: The path of the directory where the image will be saved.
        :return: The path to the saved image file.
        """
        response = requests.get(img_url)
        if 200 <= response.status_code < 300:  # Successful response
            img_ext = ".webp"
            img_filename = f"{qid}{img_ext}"
            img_path = os.path.join(save_path, img_filename)

            with open(img_path, 'wb') as img_file:
                img_file.write(response.content)
            #TODO: Catch exceptions for file writing errors and invalid directory

            return img_path

        else:
            raise ContentNotFoundException(f"Image not found at {img_url}")

    def _extract_answers(self, h1) -> (Set[str], str):
        options = []
        for elem in h1.contents:
            if getattr(elem, "name", None) == "br":
                continue
            if isinstance(elem, str):
                text = elem.strip()
                if text and len(text) > 2 and text[1] == "、" and text[0] in "ABCD":
                    options.append(text[2:].strip())
            elif getattr(elem, "name", None) == "b":
                b_text = elem.get_text(strip=True)
                if b_text and len(b_text) > 2 and b_text[1] == "、" and b_text[0] in "ABCD":
                    options.append(b_text[2:].strip())
        u = h1.find("u")
        correct_letter = u.get_text(strip=True)
        idx = ord(correct_letter) - ord("A")
        correct_answer = options[idx]
        return set(options), correct_answer

    def get_content(self, q_id: str) -> Question:
        """
        Retrieves the content of a question by its ID.
        :param q_id:
        :return: The Question object containing the question content, options,
        image, and answer.
        """
        url = self._format_url(q_id)
        webpage = self._get_webpage(url)
        return self._extract_question(q_id, webpage)


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
