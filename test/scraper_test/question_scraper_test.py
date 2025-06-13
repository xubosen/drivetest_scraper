# Library Imports
import pytest
from bs4 import BeautifulSoup
import json
import os
from PIL import Image

# Module Imports
from scraper.question import Question
from scraper.jsyks_scraper._question_scraper import QuestionScraper
from scraper.jsyks_scraper.custom_errors import JSYKSConnectionError, JSYKSContentRetrievalError

# Test constants
SAMPLE_QID = "33b74"
SAMPLE_URL = "https://tiba.jsyks.com/Post/33b74.htm"
SAMPLE_IMG_URL = "https://tp.mnks.cn/ExamPic/kmy_136.jpg"
QUESTION_IDS = ["c6219", "d150f", "ad9e0", "b5211", "cd86b"]
IMG_PATH = "db_test/img"
CONFIG_PATH = "scraper_test/site_info_test.json"

# Load sample HTML data
with open(CONFIG_PATH, "r") as file:
    site_info = json.load(file)
    SAMPLE_HTMLS = site_info["html_examples"]
SAMPLE_HTML = SAMPLE_HTMLS["four_choice"]
TF_SAMPLE_HTML = SAMPLE_HTMLS["true_false"]


# Common test helper functions
def get_h1_from_html(html):
    """Helper function to get h1 tag from HTML string"""
    soup = BeautifulSoup(html, "html.parser")
    return soup.find("h1")


class TestQuestionScraperSetup:
    """Tests for QuestionScraper initialization and configuration"""

    @pytest.fixture
    def scraper(self):
        return QuestionScraper(IMG_PATH, CONFIG_PATH)

    def test_format_url(self, scraper):
        """Test the URL formatting function."""
        expected_url = "https://tiba.jsyks.com/Post/33b74.htm"
        assert scraper._format_url(SAMPLE_QID) == expected_url, "URL formatting failed."


class TestQuestionScraperWebFetching:
    """Tests for web page fetching functionality"""

    @pytest.fixture
    def scraper(self):
        return QuestionScraper(IMG_PATH, CONFIG_PATH)

    def test_get_webpage(self, scraper):
        """Test the webpage fetching function."""
        soup = scraper._get_webpage(SAMPLE_URL)
        assert isinstance(soup, BeautifulSoup), "Webpage fetching failed."


class TestQuestionTextExtraction:
    """Tests for extracting question text from HTML"""

    @pytest.fixture
    def scraper(self):
        return QuestionScraper(IMG_PATH, CONFIG_PATH)

    def test_extract_question_text_from_sample(self, scraper):
        """Test extracting question text from sample HTML"""
        h1 = get_h1_from_html(SAMPLE_HTML)
        assert scraper._extract_question_text(h1) == "这个标志是何含义？"

    def test_extract_img_url_from_sample(self, scraper):
        """Test extracting image URL from sample HTML"""
        h1 = get_h1_from_html(SAMPLE_HTML)
        assert scraper._extract_img_url(h1) == "https://tp.mnks.cn/ExamPic/kmy_136.jpg"


class TestQuestionTypeDetection:
    """Tests for detecting question types (T/F vs multiple choice)"""

    @pytest.fixture
    def scraper(self):
        return QuestionScraper(IMG_PATH, CONFIG_PATH)

    def test_is_tf_with_four_choice(self, scraper):
        """Test if _is_tf correctly identifies four-choice questions"""
        h1 = get_h1_from_html(SAMPLE_HTML)
        assert not scraper._is_tf(h1), "Four-choice question incorrectly identified as true/false"

    def test_is_tf_with_true_false(self, scraper):
        """Test if _is_tf correctly identifies true/false questions"""
        h1 = get_h1_from_html(TF_SAMPLE_HTML)
        assert scraper._is_tf(h1), "True/false question not correctly identified"


class TestAnswerExtraction:
    """Tests for extracting answer options and correct answers"""

    @pytest.fixture
    def scraper(self):
        return QuestionScraper(IMG_PATH, CONFIG_PATH)

    def test_extract_4c(self, scraper):
        """Test extracting options from four-choice questions"""
        h1 = get_h1_from_html(SAMPLE_HTML)
        options = scraper._extract_4c(h1)

        expected = {
            "A": "注意行人",
            "B": "人行横道",
            "C": "注意儿童",
            "D": "学校区域"
        }

        assert options == expected, "Four-choice options not correctly extracted"

    def test_extract_tf(self, scraper):
        """Test extracting options from true/false questions"""
        h1 = get_h1_from_html(TF_SAMPLE_HTML)
        options = scraper._extract_tf(h1)

        expected = {"对", "错"}

        assert options == expected, "True/false options not correctly extracted"

    def test_extract_correct_for_four_choice(self, scraper):
        """Test extracting the correct answer from four-choice questions"""
        h1 = get_h1_from_html(SAMPLE_HTML)
        correct = scraper._extract_correct(h1)

        assert correct == "注意儿童", "Correct answer not properly extracted from four-choice question"

    def test_extract_correct_for_true_false(self, scraper):
        """Test extracting correct answer from true/false questions"""
        h1 = get_h1_from_html(TF_SAMPLE_HTML)
        correct = scraper._extract_correct(h1)

        assert correct == "对", "Correct answer not properly extracted from true/false question"

    def test_extract_answers_for_multiple_choice(self, scraper):
        """Test extracting answers from multiple choice questions"""
        h1 = get_h1_from_html(SAMPLE_HTML)
        options = scraper._extract_answers(h1)

        expected = {"注意行人", "人行横道", "注意儿童", "学校区域"}

        assert options == expected, "Answers not correctly extracted from multiple choice question"

    def test_extract_answers_for_true_false(self, scraper):
        """Test extracting answers from true/false questions"""
        h1 = get_h1_from_html(TF_SAMPLE_HTML)
        options = scraper._extract_answers(h1)

        expected = {"对", "错"}

        assert options == expected, "Answers not correctly extracted from true/false question"


class TestImageHandling:
    """Tests for image extraction and downloading"""

    @pytest.fixture
    def scraper(self):
        return QuestionScraper(IMG_PATH, CONFIG_PATH)

    def test_download_img(self, scraper):
        """
        Test the _download_img helper method using SAMPLE_IMG_URL.
        This test will download the image and check the file is created and
        non-empty.
        """
        # Ensure the directory exists
        os.makedirs(IMG_PATH, exist_ok=True)

        img_ext = ".webp"
        expected_filename = f"{SAMPLE_QID}{img_ext}"
        expected_path = os.path.join(IMG_PATH, expected_filename)

        # Remove file if it exists from previous runs
        if os.path.exists(expected_path):
            os.remove(expected_path)

        result_path = scraper._download_img(SAMPLE_QID, SAMPLE_IMG_URL, IMG_PATH)

        assert os.path.exists(result_path), "Image file was not created."
        assert result_path == expected_path
        assert os.path.getsize(result_path) > 0, "Downloaded image file is empty."

        # Verify the image can be opened
        try:
            with Image.open(result_path) as img:
                assert img.format in ['WEBP'], f"Invalid image format: {img.format}"
        except Exception as e:
            pytest.fail(f"Failed to open image: {str(e)}")


class TestIntegration:
    """End-to-end tests for question content retrieval"""

    @pytest.fixture
    def scraper(self):
        return QuestionScraper(IMG_PATH, CONFIG_PATH)

    def test_get_content(self, scraper):
        """
        Test the get_content method of QuestionScraper.
        This test will check if the content is correctly extracted from the
        webpage.
        """
        result = scraper.get_content(SAMPLE_QID)

        assert result._qid == SAMPLE_QID
        assert result._question == "这个标志是何含义？"
        assert result._answers == {"注意行人", "人行横道", "注意儿童", "学校区域"}
        assert result._correct_answer == "注意儿童"
        assert result._img_path == "db_test/img/33b74.webp"
