# Scrape question content, multiple choice options, and answers using requests
# and BeautifulSoup.

# Library Imports
from logging import Logger
import requests
from bs4 import BeautifulSoup, SoupStrainer
import json
from typing import Set, Dict
import os.path
import re

# Module Import
from data_storage.in_memory.question import Question
from scraper.jsyks_scraper.custom_errors import (JSYKSConnectionError,
                                                 JSYKSContentRetrievalError)


class QuestionScraper:
    """
    Scraper that retrieves the content of a question.
    """
    _img_dir: str
    _base_url: str
    _url_placeholder: str
    _questn_id_name: str
    _qid: str
    _logger: Logger

    def __init__(self, img_dir: str, config_path: str, logger: Logger):
        """
        Initializes the QuestionScraper with the site information in the json
        file.

        :param img_dir: Directory path where images will be saved
        :param config_path: Path to the JSON configuration file containing site information
        :param logger: Logger instance for logging information and errors

        === Representational Invariants ===
        - img_dir must be a valid directory path with write permissions
        - config_path must point to a valid JSON file with the required site information
        """
        logger.info("Initializing QuestionScraper")
        self._logger = logger
        self._img_dir = img_dir
        with open(config_path, "r") as file:
            site_info = json.load(file)
        self._base_url = site_info["base_url"]
        self._url_placeholder = site_info["url_placeholder"]
        self._questn_id_name = site_info["id_name"]
        self._logger.info(f"QuestionScraper initialized.")

    def _format_url(self, q_id: str) -> str:
        """
        Formats the URL for the question by replacing the placeholder with the
        question ID.

        :param q_id: The ID of the question to retrieve
        :return: The complete URL to access the question

        === Representational Invariants ===
        - q_id must be a valid question ID that can be used in the URL
        """
        return self._base_url.replace(self._url_placeholder, q_id)

    def _get_section(self, url: str) -> BeautifulSoup:
        """
        Retrieves the HTML section containing the question content.

        :param url: The URL of the page containing the question
        :return: BeautifulSoup object containing the question section
        :raises JSYKSConnectionError: If connection to the URL fails

        === Representational Invariants ===
        - url must be a valid URL that points to a page containing a question
        """
        page = requests.get(url)
        if 200 <= page.status_code < 300:
            section_filter = SoupStrainer("div", id=self._questn_id_name)
            return BeautifulSoup(page.content,
                                 'html.parser',
                                 parse_only=section_filter).find("h1")
        else:
            raise JSYKSConnectionError(f"Failed to connect to {url}. "
                                       f"Status code: {page.status_code}")

    def _get_img_path(self, sec, qid):
        """
        Gets the path to the image associated with the question.

        :param sec: BeautifulSoup object containing the question section
        :param qid: The ID of the question
        :return: Path to the downloaded image or None if no image exists

        === Representational Invariants ===
        - sec must be a valid BeautifulSoup object containing the question content
        - qid must be a valid question ID
        """
        self._logger.debug(f"Checking for image in question {qid}")
        img_url = self._extract_img_url(sec)
        if img_url is not None:
            self._logger.info(f"Image found for question {qid}, "
                              f"downloading from {img_url}")
            return self._download_img(qid, img_url, self._img_dir)
        else:
            self._logger.debug(f"No image found for question {qid}")
            return None

    def _extract_img_url(self, sec) -> str | None:
        """
        Extracts the image URL from the question section if it exists.

        :param sec: BeautifulSoup object containing the question section
        :return: URL of the image as a string, or None if no image is found

        === Representational Invariants ===
        - sec must be a valid BeautifulSoup object containing the question content
        """
        img = sec.find("img")
        if img:
            url = img["src"]
            return url
        return None

    def _download_img(self, qid:str, img_url: str, save_path: str) -> str:
        """
        Download the image from the given URL and save it to the specified
        path.

        :param qid: The question ID, used to create a unique filename.
        :param img_url: The URL of the image to download.
        :param save_path: The path of the directory where the image will be saved.
        :return: The path to the saved image file.
        :raises JSYKSConnectionError: If downloading the image fails

        === Representational Invariants ===
        - img_url is a valid URL pointing to an image resource.
        - save_path is a valid directory path where the image can be saved.
        """
        response = requests.get(img_url)
        if 200 <= response.status_code < 300:  # Successful response
            img_path = os.path.join(save_path, f"{qid}.webp")
            with open(img_path, 'wb') as img_file:
                img_file.write(response.content)
            return img_path
        else:
            raise JSYKSConnectionError(f"Failed to download image from "
                                       f"{img_url}. "
                                       f"Status code: {response.status_code}")

    def _get_q_txt(self, sec: BeautifulSoup) -> str:
        """
        Extracts the question text from the HTML section.

        :param sec: BeautifulSoup object containing the question section
        :return: The text of the question as a string

        === Representational Invariants ===
        - sec must be a valid BeautifulSoup object containing the question content
        - The question section must contain an anchor tag with the question text
        """
        return sec.find("a").get_text()

    def _get_ops(self, sec: BeautifulSoup) -> Set[str]:
        """
        Return the set of options of answers for the question.

        :param sec: BeautifulSoup object containing the question section
        :return: Set of possible answers for the question

        === Representational Invariants ===
        - sec must be a valid BeautifulSoup object containing the question content
        - The question must be either a true/false or a four-choice question
        """
        self._logger.debug("Getting answer options for question")
        if self._is_tf(sec):
            self._logger.debug("Question is true/false type")
            return {"对", "错"}
        else:
            self._logger.debug("Question is multiple choice type")
            letter_to_answer = self._extract_4c(sec)
            options = set(letter_to_answer.values())
            self._logger.debug(f"Extracted {len(options)} answer options")
            return options

    def _is_tf(self, sec: BeautifulSoup) -> bool:
        """
        Return True if the question is a True/False question and False if it is
        a four-choice question.

        :param sec: BeautifulSoup object containing the question section
        :return: True if the question is true/false, False otherwise

        === Representational Invariants ===
        - sec must be a valid BeautifulSoup object containing the question
        content
        - The question format must be either true/false or four-choice
        """
        # Look for 答案：<u>对</u> or 答案：<u>错</u>
        return "答案：<u>对</u>" in str(sec) or "答案：<u>错</u>" in str(sec)

    def _extract_4c(self, sec: BeautifulSoup) -> Dict[str, str]:
        """
        Return the four choices of the question as a dictionary of letters to
        answers.

        :param sec: BeautifulSoup object containing the question section
        :return: Dictionary mapping option letters (A-D) to their corresponding
        answer texts

        === Representational Invariants ===
        - sec must be a valid BeautifulSoup object containing the question
        content
        - The question must be a four-choice question with options labeled A
        through D
        - Each option must follow the pattern "X、[answer text]" where X is a
        letter A-D
        """
        pattern = re.compile(r'(?:<b>)?([A-D])、(.*?)(?:</b>)?<br/>')
        options = {}
        for letter, answer in pattern.findall(str(sec)):
            options[letter.strip()] = answer.strip()
        return options

    def _get_ans(self, sec: BeautifulSoup) -> str:
        """
        Return the correct answer for the question.

        :param sec: BeautifulSoup object containing the question section
        :return: The correct answer as a string
        :raises JSYKSContentRetrievalError: If the correct answer cannot be determined

        === Representational Invariants ===
        - sec must be a valid BeautifulSoup object containing the question content
        - The correct answer must be marked in the HTML with <u> tags
        - For multiple choice questions, the answer must be one of the options A-D
        """
        if self._is_tf(sec):
            if "答案：<u>对</u>" in str(sec):
                return "对"
            elif "答案：<u>错</u>" in str(sec):
                return "错"
            else:
                raise JSYKSContentRetrievalError(
                    "Could not determine correct answer for T/F question")
        else:
            letter_to_answer = self._extract_4c(sec)

            # Look between the <u> tags for the correct answer
            match = re.search(r'答案：<u>([A-D])</u>', str(sec))
            correct_letter = match.group(1)

            return letter_to_answer[correct_letter]

    def get_question(self, qid: str) -> Question:
        """
        Retrieves a question by its ID

        :param qid: The ID of the question to retrieve
        :return: A Question object containing all the question data
        :raises JSYKSConnectionError: If connection to the question URL fails
        :raises JSYKSContentRetrievalError: If the question content cannot be
        parsed
        """
        self._logger.info(f"Retrieving question with ID: {qid}")
        try:
            url = self._format_url(qid)
            section = self._get_section(url)

            question_text = self._get_q_txt(section)
            answers = self._get_ops(section)
            correct_answer = self._get_ans(section)
            img_path = self._get_img_path(section, qid)

            question = Question(
                qid=qid,
                question=question_text,
                answers=answers,
                correct_answer=correct_answer,
                img_path=img_path
            )

            self._logger.info(f"Successfully retrieved question {qid}")
            return question
        except (JSYKSConnectionError, JSYKSContentRetrievalError) as e:
            self._logger.error(f"Failed to retrieve question {qid}: {str(e)}")
            raise
        except Exception as e:
            self._logger.critical(f"Unexpected error retrieving question "
                                  f"{qid}: {str(e)}")
            raise JSYKSContentRetrievalError(f"Unexpected error: {str(e)}")
