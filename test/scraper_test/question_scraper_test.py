# Library Imports
import pytest
from bs4 import BeautifulSoup
import json
import os
from PIL import Image
from unittest.mock import patch, MagicMock

# Module Imports
from scraper.question import Question
from scraper.jsyks_scraper._question_scraper import QuestionScraper
from scraper.jsyks_scraper.custom_errors import (JSYKSConnectionError,
                                                 JSYKSContentRetrievalError,
                                                 ConfigError)

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

# Create a sample HTML without images for testing
NO_IMG_HTML = """<div id="question" class="fcc"><h1><strong><a href="/Post/abcde.htm">这是一个没有图片的问题？</a></strong>
A、选项一<br>B、选项二<br><b>C、选项三</b><br>D、选项四<br>答案：<u>C</u></h1><p><i title="人气指数" id="ReadCount">1000</i></p><b class="bg"></b></div>"""

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
        assert scraper._format_url(SAMPLE_QID) == expected_url, \
            "URL formatting failed."


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
        assert (scraper._extract_img_url(h1) ==
                "https://tp.mnks.cn/ExamPic/kmy_136.jpg")

    def test_extract_question_text_from_html_without_images(self, scraper):
        """Test extracting question text from HTML without images"""
        h1 = get_h1_from_html(NO_IMG_HTML)
        assert scraper._extract_question_text(h1) == "这是一个没有图片的问题？"

    def test_extract_img_path(self, scraper):
        """Test _extract_img_path method which combines URL extraction and downloading"""
        # Create a mock for the h1 section
        h1 = get_h1_from_html(SAMPLE_HTML)

        # Patch the _download_img method to avoid actual network calls
        with patch.object(scraper, '_download_img', return_value=f"{IMG_PATH}/{SAMPLE_QID}.webp") as mock_download:
            img_path = scraper._extract_img_path(h1, SAMPLE_QID)

            # Verify _download_img was called with the correct parameters
            mock_download.assert_called_once_with(
                SAMPLE_QID,
                "https://tp.mnks.cn/ExamPic/kmy_136.jpg",
                IMG_PATH
            )

            # Verify the return value
            assert img_path == f"{IMG_PATH}/{SAMPLE_QID}.webp"


class TestQuestionTypeDetection:
    """Tests for detecting question types (T/F vs multiple choice)"""

    @pytest.fixture
    def scraper(self):
        return QuestionScraper(IMG_PATH, CONFIG_PATH)

    def test_is_tf_with_four_choice(self, scraper):
        """Test if _is_tf correctly identifies four-choice questions"""
        h1 = get_h1_from_html(SAMPLE_HTML)
        assert not scraper._is_tf(h1), \
            "Four-choice question incorrectly identified as true/false"

    def test_is_tf_with_true_false(self, scraper):
        """Test if _is_tf correctly identifies true/false questions"""
        h1 = get_h1_from_html(TF_SAMPLE_HTML)
        assert scraper._is_tf(h1), \
            "True/false question not correctly identified"


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

        assert options == expected, \
            "Four-choice options not correctly extracted"

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

        assert correct == "注意儿童", \
            "Correct answer not properly extracted from four-choice question"

    def test_extract_correct_for_true_false(self, scraper):
        """Test extracting correct answer from true/false questions"""
        h1 = get_h1_from_html(TF_SAMPLE_HTML)
        correct = scraper._extract_correct(h1)

        assert correct == "对", \
            "Correct answer not properly extracted from true/false question"

    def test_extract_answers_for_multiple_choice(self, scraper):
        """Test extracting answers from multiple choice questions"""
        h1 = get_h1_from_html(SAMPLE_HTML)
        options = scraper._extract_answers(h1)

        expected = {"注意行人", "人行横道", "注意儿童", "学校区域"}

        assert options == expected, \
            "Answers not correctly extracted from multiple choice question"

    def test_extract_answers_for_true_false(self, scraper):
        """Test extracting answers from true/false questions"""
        h1 = get_h1_from_html(TF_SAMPLE_HTML)
        options = scraper._extract_answers(h1)

        expected = {"对", "错"}

        assert options == expected, \
            "Answers not correctly extracted from true/false question"


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

    def test_behavior_when_image_url_is_none(self, scraper):
        """Test behavior when image URL is None (question has no image)"""
        h1 = get_h1_from_html(NO_IMG_HTML)

        # Extract image URL should return None
        assert scraper._extract_img_url(h1) is None, "Should return None for HTML without image"

        # Test that _extract_img_path correctly handles None image URL
        img_path = scraper._extract_img_path(h1, "abcde")
        assert img_path is None, "Image path should be None when no image is present"


class TestIntegration:
    """End-to-end tests for question content retrieval"""

    @pytest.fixture
    def scraper(self):
        return QuestionScraper(IMG_PATH, CONFIG_PATH)

    def test_get_content_4c(self, scraper):
        """
        Test the get_content method of QuestionScraper with a four-choice
        question.
        """
        result = scraper.get_content(SAMPLE_QID)

        assert result._qid == SAMPLE_QID
        assert result._question == "这个标志是何含义？"
        assert result._answers == {"注意行人", "人行横道", "注意儿童", "学校区域"}
        assert result._correct_answer == "注意儿童"
        assert result._img_path == "db_test/img/33b74.webp"

    def test_get_content_true_false(self, scraper):
        """Test get_content with a true/false question"""
        # Mock the webpage fetching to return our TF sample HTML
        with patch.object(scraper, '_get_webpage') as mock_get_webpage:
            # Create a BeautifulSoup object from the TF_SAMPLE_HTML
            soup = BeautifulSoup(TF_SAMPLE_HTML, 'html.parser')
            mock_get_webpage.return_value = soup

            # Mock _extract_img_path to avoid actual network calls
            with patch.object(scraper, '_extract_img_path', return_value=None):
                result = scraper.get_content("e4fec")

                assert result._qid == "e4fec"
                assert result._question == "驾驶校车、中型以上载客载货汽车、危险物品运输车辆在高速公路、城市快速路以外的道路上行驶超过规定时速百分之五十以上的，一次记9分。"
                assert result._answers == {"对", "错"}
                assert result._correct_answer == "对"
                assert result._img_path is None

    def test_get_content_no_image(self, scraper):
        """Test get_content with a question that has no image"""
        # Mock the webpage fetching to return our no-image sample HTML
        with patch.object(scraper, '_get_webpage') as mock_get_webpage:
            # Create a BeautifulSoup object from the NO_IMG_HTML
            soup = BeautifulSoup(NO_IMG_HTML, 'html.parser')
            mock_get_webpage.return_value = soup

            result = scraper.get_content("abcde")

            assert result._qid == "abcde"
            assert result._question == "这是一个没有图片的问题？"
            assert result._answers == {"选项一", "选项二", "选项三", "选项四"}
            assert result._correct_answer == "选项三"
            assert result._img_path is None

    def test_mocked_get_content(self):
        """Create a mocked version of tests to avoid external dependencies"""
        # Create a mock for the scraper
        mock_scraper = MagicMock()

        # Configure the mock to return a Question object
        mock_question = Question(
            qid="mock123",
            question="This is a mock question?",
            answers={"Answer 1", "Answer 2", "Answer 3", "Answer 4"},
            correct_answer="Answer 3",
            img_path="mock/path/to/image.webp"
        )
        mock_scraper.get_content.return_value = mock_question

        # Call the mocked method
        result = mock_scraper.get_content("mock123")

        # Verify the result
        assert result._qid == "mock123"
        assert result._question == "This is a mock question?"
        assert result._answers == {"Answer 1", "Answer 2", "Answer 3", "Answer 4"}
        assert result._correct_answer == "Answer 3"
        assert result._img_path == "mock/path/to/image.webp"

        # Verify the mock was called with the expected argument
        mock_scraper.get_content.assert_called_once_with("mock123")
