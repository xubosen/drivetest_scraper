# Scrape question content, multiple choice options, and answers using requests
# and BeautifulSoup.

# Library Imports
import requests
from bs4 import BeautifulSoup, SoupStrainer
import json
from typing import Set, Dict
import os.path
import re

# Module Import
from scraper.question import Question
from scraper.jsyks_scraper.custom_errors import (JSYKSConnectionError,
                                                 JSYKSContentRetrievalError,
                                                 ConfigError)


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
        # Error handling for a missing config file
        if (not os.path.exists(self._config_path) or
                not os.path.isfile(self._config_path)):
            raise ConfigError(f"Configuration file is missing or corrupted:"
                              f" {self._config_path}")
        else:
            file = open(self._config_path, "r")

        # Error handling for JSON parsing errors
        try:
            site_info = json.load(file)
            file.close()
        except json.JSONDecodeError as e:
            file.close()
            raise ConfigError(f"Error parsing JSON configuration file: {e}")

        # Check that the required keys exist in the loaded JSON
        site_info_keys = {"url", "url_placeholder", "div_id"}
        if site_info_keys.issubset(site_info.keys()):
            self._generic_url = site_info["url"]
            self._url_placeholder = site_info["url_placeholder"]
            self._questn_div_id = site_info["div_id"]
        else:
            raise ConfigError("Configuration file is missing required keys: "
                              + str(site_info_keys))

    def _format_url(self, q_id: str) -> str:
        """
        Return the correct url to request for by replacing the placeholder with
        the question ID.
        :param q_id:
        :return:

        === Representational Invariants ===
        - q_id is a valid question ID
        """
        return self._generic_url.replace(self._url_placeholder, q_id)

    def _get_webpage(self, url: str) -> BeautifulSoup:
        """
        Fetches the webpage content from the given URL.
        :param url: The URL of the webpage to scrape.
        :return: BeautifulSoup object containing the parsed HTML content.
        """
        # Handle unexpected request issues like incorrect URLs
        try:
            response = requests.get(url)
        except requests.RequestException as e:
            raise JSYKSConnectionError(f"Failed to connect to {url}. "
                                       f"Error: {e}")

        parse_filter = SoupStrainer(id=self._questn_div_id)

        if 200 <= response.status_code < 300: # Successful response
            return BeautifulSoup(response.content,
                                 'html.parser',
                                 parse_only=parse_filter)
        else:
            raise JSYKSConnectionError(f"Failed to connect to {url}. "
                                       f"Status code: {response.status_code}")

    def _extract_img_path(self, html_section, qid):
        img_url = self._extract_img_url(html_section)
        if img_url is not None:
            img_path = self._download_img(qid, img_url, self._img_dir)
        else:
            img_path = None
        return img_path

    def _extract_question_text(self, html_section) -> str:
        if html_section is None:
            raise JSYKSContentRetrievalError("HTML section is None, cannot extract question text")

        strong = html_section.find("strong")
        if strong is None:
            raise JSYKSContentRetrievalError("Could not find <strong> tag in HTML section")

        a = strong.find("a")
        if a is None:
            raise JSYKSContentRetrievalError("Could not find <a> tag in HTML section")

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

        === Representational Invariants ===
        - img_url is a valid URL pointing to an image resource.
        - save_path is a valid directory path where the image can be saved.
        """
        response = requests.get(img_url)
        if 200 <= response.status_code < 300:  # Successful response
            img_ext = ".webp"
            img_filename = f"{qid}{img_ext}"
            img_path = os.path.join(save_path, img_filename)

            with open(img_path, 'wb') as img_file:
                img_file.write(response.content)

            return img_path

        else:
            raise JSYKSContentRetrievalError(f"Image not found at {img_url}")

    def _extract_answers(self, header: BeautifulSoup) -> Set[str]:
        """
        Return the set of answers for the question.
        """
        if self._is_tf(header):
            return self._extract_tf(header)
        else:
            letter_to_answer = self._extract_4c(header)
            return set(letter_to_answer.values())

    def _is_tf(self, header: BeautifulSoup) -> bool:
        """
        Return True if the question is a True/False question and False if it is a
        four-choice question.
        """
        header_str = str(header)
        # Look for 答案：<u>对</u> or 答案：<u>错</u>
        return "答案：<u>对</u>" in header_str or "答案：<u>错</u>" in header_str

    def _extract_4c(self, header: BeautifulSoup) -> Dict[str, str]:
        """
        Return the four choices of the question as a dictionary of letters to
        answers.
        """
        header_str = str(header)
        pattern = re.compile(r'(?:<b>)?([A-D])、(.*?)(?:</b>)?<br/>')
        options = {}
        matches = pattern.findall(header_str)

        # Validate that we have matches in the expected format
        if not matches:
            raise JSYKSContentRetrievalError("Could not find multiple-choice "
                                             "options in the expected format")
        elif len(matches) != 4:
            raise JSYKSContentRetrievalError(f"Expected 4 options, but found "
                                             f"{len(matches)}")

        for letter, answer in matches:
            options[letter.strip()] = answer.strip()

        # Verify that we have all expected letters (A, B, C, D)
        expected_letters = {"A", "B", "C", "D"}
        if set(options.keys()) != expected_letters:
            raise JSYKSContentRetrievalError("Options do not match expected "
                                             "letters A, B, C, D")

        return options

    def _extract_tf(self, header: BeautifulSoup) -> Set[str]:
        """
        Return the two choices of the question as a set
        """
        return {"对", "错"}

    def _extract_correct(self, header: BeautifulSoup) -> str:
        """
        Return the correct answer for the question.

        :param header: The BeautifulSoup object containing the question.
        """
        if self._is_tf(header):
            if "答案：<u>对</u>" in str(header):
                return "对"
            elif "答案：<u>错</u>" in str(header):
                return "错"
            else:
                raise JSYKSContentRetrievalError(
                    "Could not determine correct answer for T/F question")
        else:
            letter_to_answer = self._extract_4c(header)

            # Look between the <u> tags for the correct answer
            correct_match = re.search(r'答案：<u>([A-D])</u>', str(header))

            # Handle regex pattern match failures
            if not correct_match:
                raise JSYKSContentRetrievalError(
                    "Could not find correct answer marker in expected format")

            correct_letter = correct_match.group(1)

            # Handle when correct_letter is not in letter_to_answer
            if correct_letter not in letter_to_answer:
                raise JSYKSContentRetrievalError(
                    f"Correct answer letter '{correct_letter}' not found in the"
                    f"answer options")

            return letter_to_answer[correct_letter]

    def get_content(self, qid: str) -> Question:
            """
            Retrieves the content of a question by its ID.
            :param qid:
            :return: The Question object created
            """
            url = self._format_url(qid)
            webpage = self._get_webpage(url)
            section = webpage.find("h1")

            # Validate that header exists
            if section is None:
                raise JSYKSContentRetrievalError(f"Could not find h1 tag in "
                                                 f"question {qid}")

            return Question(
                qid=qid,
                question=self._extract_question_text(section),
                answers=self._extract_answers(section),
                correct_answer=self._extract_correct(section),
                img_path=self._extract_img_path(section, qid)
            )
