# Library Imports
import pytest
from bs4 import BeautifulSoup
import json
import os
from PIL import Image

# Module Imports
from scraper.question import Question
from scraper.jsyks_scraper._question_scraper import QuestionScraper

SAMPLE_QID = "33b74"

SAMPLE_URL = "https://tiba.jsyks.com/Post/33b74.htm"
SAMPLE_IMG_URL = "https://tp.mnks.cn/ExamPic/kmy_136.jpg"

QUESTION_IDS = ["c6219", "d150f", "ad9e0", "b5211", "cd86b"]
IMG_PATH = "db_test/img"
CONFIG_PATH = "scraper_test/site_info_test.json"
with open(CONFIG_PATH, "r") as file:
    site_info = json.load(file)
    SAMPLE_HTMLS = site_info["html_examples"]
SAMPLE_HTML = SAMPLE_HTMLS["four_choice"]
TF_SAMPLE_HTML = SAMPLE_HTMLS["true_false"]

class TestQuestionScraper:
    """
    Test class for the QuestionScraper.
    """
    scraper: QuestionScraper
    url: str
    webpage: BeautifulSoup | None

    # Set up attributes
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """
        Setup method to initialize the QuestionScraper before each test.
        """
        self.scraper = QuestionScraper(IMG_PATH, CONFIG_PATH)
        self.url = SAMPLE_URL
        self.webpage = None

    def test_format_url(self):
        """
        Test the URL formatting function.
        """
        expected_url = "https://tiba.jsyks.com/Post/33b74.htm"
        assert self.scraper._format_url(SAMPLE_QID) == expected_url, \
            "URL formatting failed."

    def test_get_webpage(self):
        """
        Test the webpage fetching function.
        """
        soup = self.scraper._get_webpage(self.url)
        assert isinstance(soup, BeautifulSoup), "Webpage fetching failed."
        if isinstance(soup, BeautifulSoup):
            self.webpage = soup

    def get_h1(self, html=SAMPLE_HTML):
        soup = BeautifulSoup(html, "html.parser")
        return soup.find("h1")

    def test__extract_question_text_from_sample(self):
        assert self.scraper._extract_question_text(
            self.get_h1()
        ) == "这个标志是何含义？"

    def test__extract_img_url_from_sample(self):
        scraper = self.scraper
        h1 = self.get_h1()
        assert (scraper._extract_img_url(h1) ==
                "https://tp.mnks.cn/ExamPic/kmy_136.jpg")

    def test__extract_answers_from_sample(self):
        scraper = self.scraper
        h1 = self.get_h1()
        options = scraper._extract_answers(h1)
        assert options == {"注意行人", "人行横道", "注意儿童", "学校区域"}

    def test__is_tf_with_four_choice(self):
        """Test if _is_tf correctly identifies four-choice questions"""
        h1 = self.get_h1(SAMPLE_HTML)
        assert not self.scraper._is_tf(h1), "Four-choice question incorrectly identified as true/false"

    def test__is_tf_with_true_false(self):
        """Test if _is_tf correctly identifies true/false questions"""
        h1 = self.get_h1(TF_SAMPLE_HTML)
        assert self.scraper._is_tf(h1), "True/false question not correctly identified"

    def test__extract_4c(self):
        """Test extracting options from four-choice questions"""
        h1 = self.get_h1(SAMPLE_HTML)
        options = self.scraper._extract_4c(h1)

        expected = {
            "A": "注意行人",
            "B": "人行横道",
            "C": "注意儿童",
            "D": "学校区域"
        }

        assert options == expected, "Four-choice options not correctly extracted"

    def test__extract_tf(self):
        """Test extracting options from true/false questions"""
        h1 = self.get_h1(TF_SAMPLE_HTML)
        options = self.scraper._extract_tf(h1)

        expected = {"对", "错"}

        assert options == expected, "True/false options not correctly extracted"

    def test__extract_correct_for_four_choice(self):
        """Test extracting the correct answer from four-choice questions"""
        h1 = self.get_h1(SAMPLE_HTML)
        correct = self.scraper._extract_correct(h1)

        assert correct == "注意儿童", ("Correct answer not properly extracted "
                                       "from four-choice question")

    def test__extract_correct_for_true_false(self):
        """Test extracting correct answer from true/false questions"""
        h1 = self.get_h1(TF_SAMPLE_HTML)
        correct = self.scraper._extract_correct(h1)

        assert correct == "对", ("Correct answer not properly extracted from "
                                 "true/false question")

    def test__extract_answers_for_true_false(self):
        """Test extracting answers from true/false questions"""
        h1 = self.get_h1(TF_SAMPLE_HTML)
        options = self.scraper._extract_answers(h1)

        expected = {"对", "错"}

        assert options == expected, ("Answers not correctly extracted from "
                                     "true/false question")

    def test__download_img(self):
        """
        Test the _download_img helper method using SAMPLE_IMG_URL.
        This test will download the image and check the file is created and
        non-empty.
        """
        img_ext = ".webp"
        expected_filename = f"{SAMPLE_QID}{img_ext}"
        expected_path = os.path.join(IMG_PATH, expected_filename)

        # Ensure the directory exists
        os.makedirs(IMG_PATH, exist_ok=True)

        # Remove file if it exists from previous runs
        if os.path.exists(expected_path):
            os.remove(expected_path)

        result_path = self.scraper._download_img(SAMPLE_QID, SAMPLE_IMG_URL,
                                                 IMG_PATH)

        assert os.path.exists(result_path), "Image file was not created."
        assert result_path == expected_path
        assert os.path.getsize(result_path) > 0, \
            "Downloaded image file is empty."

        # Verify the image can be opened
        try:
            with Image.open(result_path) as img:
                assert img.format in ['WEBP'], (f"Invalid image format"
                                                f": {img.format}")
        except Exception as e:
            pytest.fail(f"Failed to open image: {str(e)}")

    def test_get_content(self):
        """
        Test the get_content method of QuestionScraper.
        This test will check if the content is correctly extracted from the
        webpage.
        """
        result = self.scraper.get_content(SAMPLE_QID)

        assert result._qid == SAMPLE_QID
        assert result._question == "这个标志是何含义？"
        assert result._answers == {"注意行人", "人行横道", "注意儿童", "学校区域"}
        assert result._correct_answer == "注意儿童"
        assert result._img_path == "db_test/img/33b74.webp"
