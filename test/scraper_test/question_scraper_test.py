# Library Imports
import pytest
from bs4 import BeautifulSoup
import json
import os
import logging

# Module Imports
from scraper.jsyks_scraper._question_scraper import QuestionScraper
from src.data_storage.in_memory.question import Question
from scraper.jsyks_scraper.custom_errors import (JSYKSConnectionError,
                                                 JSYKSContentRetrievalError,
                                                 ConfigError)

# Constants
IMG_SAVE_PATH = "qb_test/img"
CONFIG_PATH = "scraper_test/q_test_config.json"
TEST_MATERIAL_PATH = "scraper_test/q_test_material"

# Load q_test_material.json into constants
Q_TEST_MATERIAL_PATH = "scraper_test/q_test_material.json"
with open(Q_TEST_MATERIAL_PATH, "r", encoding="utf-8") as f:
    Q_TEST_MATERIAL = json.load(f)

SAMPLE_QIDS = Q_TEST_MATERIAL["SAMPLE_QIDS"]
SAMPLE_URLS = Q_TEST_MATERIAL["SAMPLE_URLS"]
SAMPLE_IMG_URLS = Q_TEST_MATERIAL["SAMPLE_IMG_URLS"]
SAMPLE_SECTION_HTML = Q_TEST_MATERIAL["SAMPLE_SECTION_HTML"]

# Logger setup
LOG_PATH = "test_logs"
if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)

LOGGER = logging.getLogger("question_scraper_test")
LOGGER.setLevel(logging.DEBUG)
log_file_handler = logging.FileHandler(
    os.path.join(LOG_PATH, "question_scraper_test.log"),
    encoding="utf-8")
log_file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
log_file_handler.setFormatter(formatter)
LOGGER.addHandler(log_file_handler)


class TestFormatUrl:
    """Unit tests for the _format_url method of QuestionScraper, which generates
    the correct URL for a given question ID."""

    def test_format_url_replaces_placeholder(self):
        """
        Test that _format_url correctly replaces the placeholder with the question ID.

        Uses SAMPLE_QIDS and SAMPLE_URLS from the test material to verify that
        the generated URLs match the expected URLs for various question IDs.
        """
        scraper = QuestionScraper(IMG_SAVE_PATH, CONFIG_PATH, LOGGER)
        # Test for each category
        for category in SAMPLE_QIDS:
            for qid, expected_url in zip(SAMPLE_QIDS[category], SAMPLE_URLS[category]):
                assert scraper._format_url(qid) == expected_url

class TestGetSection:
    """Unit tests for the _get_section method of QuestionScraper, which
    retrieves the HTML section containing the question."""

    def test_get_section_returns_h1(self):
        """
        Test that _get_section returns a BeautifulSoup object containing the
        question section.

        Make real requests to the URLs in SAMPLE_URLS and check that the
        method returns a section wrapped in h1 tags
        """
        scraper = QuestionScraper(IMG_SAVE_PATH, CONFIG_PATH, LOGGER)
        # Only test a small sample to avoid excessive requests
        sample_qids = ["eb681", "51b33", "d6fc4", "b85e0"]
        for qid in sample_qids:
            url = scraper._format_url(qid)
            sec = scraper._get_section(url)
            assert sec is not None
            assert sec.name == "h1", \
                f"Expected <h1> tag, got {sec.name} for qid {qid}"

    def test_get_section_samples(self):
        """
        Test that _get_section returns the Sample Sections when the
        corresponding url is used.
        """
        scraper = QuestionScraper(IMG_SAVE_PATH, CONFIG_PATH, LOGGER)
        for qid, html in SAMPLE_SECTION_HTML.items():
            url = scraper._format_url(qid)
            sec = scraper._get_section(url)
            assert sec is not None
            assert str(sec) == html

class TestGetImgPath:
    """Unit tests for the _get_img_path method of QuestionScraper, which
    determines the image path for a question if an image exists."""

    def test_get_img_path_with_image_tf(self):
        """
        Test that _get_img_path returns the correct image path when an image
        exists in a true/false question.
        """
        scraper = QuestionScraper(IMG_SAVE_PATH, CONFIG_PATH, LOGGER)
        # Use a TF question with image from SAMPLE_IMG_URLS and SAMPLE_SECTION_HTML
        for qid in SAMPLE_QIDS["SAMPLE_TF_IMG"]:
            if qid in SAMPLE_IMG_URLS and qid in SAMPLE_SECTION_HTML:
                html = SAMPLE_SECTION_HTML[qid]
                soup = BeautifulSoup(html, "html.parser")
                h1 = soup.find("h1")
                img_path = scraper._get_img_path(h1, qid)
                assert img_path is not None
                assert os.path.exists(img_path)
                # Clean up
                os.remove(img_path)

    def test_get_img_path_with_image_4c(self):
        """
        Test that _get_img_path returns the correct image path when an image
        exists in a four-choice question.
        """
        scraper = QuestionScraper(IMG_SAVE_PATH, CONFIG_PATH, LOGGER)
        for qid in SAMPLE_QIDS["SAMPLE_4C_IMG"]:
            if qid in SAMPLE_IMG_URLS and qid in SAMPLE_SECTION_HTML:
                html = SAMPLE_SECTION_HTML[qid]
                soup = BeautifulSoup(html, "html.parser")
                h1 = soup.find("h1")
                img_path = scraper._get_img_path(h1, qid)
                assert img_path is not None
                assert os.path.exists(img_path)
                # Clean up
                os.remove(img_path)

    def test_get_img_path_without_image_tf(self):
        """
        Test that _get_img_path returns None when no image exists in a
        true/false question.
        """
        scraper = QuestionScraper(IMG_SAVE_PATH, CONFIG_PATH, LOGGER)
        for qid in SAMPLE_QIDS["SAMPLE_TF_NO_IMG"]:
            if qid in SAMPLE_SECTION_HTML:
                html = SAMPLE_SECTION_HTML[qid]
                soup = BeautifulSoup(html, "html.parser")
                h1 = soup.find("h1")
                img_path = scraper._get_img_path(h1, qid)
                assert img_path is None

    def test_get_img_path_without_image_4c(self):
        """
        Test that _get_img_path returns None when no image exists in a
        four-choice question.
        """
        scraper = QuestionScraper(IMG_SAVE_PATH, CONFIG_PATH, LOGGER)
        for qid in SAMPLE_QIDS["SAMPLE_4C_NO_IMG"]:
            if qid in SAMPLE_SECTION_HTML:
                html = SAMPLE_SECTION_HTML[qid]
                soup = BeautifulSoup(html, "html.parser")
                h1 = soup.find("h1")
                img_path = scraper._get_img_path(h1, qid)
                assert img_path is None

class TestExtractImgUrl:
    """Unit tests for the _extract_img_url method of QuestionScraper, which
    extracts the image URL from the question section."""

    def test_extract_img_url_present(self):
        """
        Test that _extract_img_url returns the correct image URL if present.

        Uses SAMPLE_SECTION_HTML and SAMPLE_IMG_URLS to check that the correct
        image URL is extracted from a section containing an image.
        """
        scraper = QuestionScraper(IMG_SAVE_PATH, CONFIG_PATH, LOGGER)
        for qid, img_url in SAMPLE_IMG_URLS.items():
            html = SAMPLE_SECTION_HTML.get(qid)
            if html:
                soup = BeautifulSoup(html, "html.parser")
                h1 = soup.find("h1")
                extracted_url = scraper._extract_img_url(h1)
                assert extracted_url == img_url

    def test_extract_img_url_absent(self):
        """
        Test that _extract_img_url returns None if no image is present.

        Uses SAMPLE_SECTION_HTML for a question without an image to verify that
        None is returned.
        """
        scraper = QuestionScraper(IMG_SAVE_PATH, CONFIG_PATH, LOGGER)
        for qid, html in SAMPLE_SECTION_HTML.items():
            if (qid in SAMPLE_QIDS["SAMPLE_TF_NO_IMG"] or
                    qid in SAMPLE_QIDS["SAMPLE_4C_NO_IMG"]):
                soup = BeautifulSoup(html, "html.parser")
                h1 = soup.find("h1")
                extracted_url = scraper._extract_img_url(h1)
                assert extracted_url is None

class TestGetQTxt:
    """Unit tests for the _get_q_txt method of QuestionScraper, which extracts
    the question text from the section."""

    def test_get_q_txt_extracts_text(self):
        """
        Test that _get_q_txt extracts the question text from the section.

        Uses SAMPLE_SECTION_HTML to provide HTML for both true/false and four-choice
        questions and checks that the extracted text matches the expected question.
        """
        scraper = QuestionScraper(IMG_SAVE_PATH, CONFIG_PATH, LOGGER)
        expected_texts = {
            "b37fe": "驾驶机动车遇前方机动车停车排队或者缓慢行驶时，借道超车或者占用对面车道、穿插等候车辆的，一次记1分。",
            "89195": "如图所示，在环岛交叉路口发生的交通事故中，应由A车负全部责任。",
            "d548b": "驾驶机动车在高速公路上发生故障时，以下做法正确的是什么？",
            "10d89": "在路口直行时，遇这种情形如何通行？"
        }
        for qid in SAMPLE_SECTION_HTML.keys():
            html = SAMPLE_SECTION_HTML[qid]
            soup = BeautifulSoup(html, "html.parser")
            h1 = soup.find("h1")
            q_txt = scraper._get_q_txt(h1)
            assert q_txt == expected_texts[qid]

class TestGetOps:
    """Unit tests for the _get_ops method of QuestionScraper, which returns the
    set of possible answers for a question."""

    def test_get_ops_true_false(self):
        """
        Test that _get_ops returns correct options for true/false questions.

        Uses SAMPLE_SECTION_HTML for true/false questions to verify that the
        returned set is {"对", "错"}.
        """
        scraper = QuestionScraper(IMG_SAVE_PATH, CONFIG_PATH, LOGGER)
        for qid in ["b37fe", "89195"]:
            html = SAMPLE_SECTION_HTML[qid]
            soup = BeautifulSoup(html, "html.parser")
            h1 = soup.find("h1")
            ops = scraper._get_ops(h1)
            assert ops == {"对", "错"}

    def test_get_ops_four_choice(self):
        """
        Test that _get_ops returns correct options for four-choice questions.

        Uses SAMPLE_SECTION_HTML for four-choice questions to verify that the
        returned set matches the expected options.
        """
        scraper = QuestionScraper(IMG_SAVE_PATH, CONFIG_PATH, LOGGER)
        expected_ops = {
            "d548b": {
                "拦截过往车辆帮助拖车",
                "借用其他机动车牵引",
                "车上人员应当坐在车内等待救援",
                "开启危险报警闪光灯，并在来车方向150米外设置警告标志"
            },
            "10d89": {
                "让左方道路车辆先行",
                "让右方道路车辆先行",
                "直接加速直行通过",
                "开启危险报警闪光灯通行"
            }
        }
        for qid in ["d548b", "10d89"]:
            html = SAMPLE_SECTION_HTML[qid]
            soup = BeautifulSoup(html, "html.parser")
            h1 = soup.find("h1")
            ops = scraper._get_ops(h1)
            assert ops == expected_ops[qid]

class TestIsTF:
    """Unit tests for the _is_tf method of QuestionScraper, which determines if
    a question is true/false type."""

    def test_is_tf_true_false(self):
        """
        Test that _is_tf returns True for true/false questions.

        Uses SAMPLE_SECTION_HTML for true/false questions to verify that the
        method returns True.
        """
        scraper = QuestionScraper(IMG_SAVE_PATH, CONFIG_PATH, LOGGER)
        for qid in ["b37fe", "89195"]:
            html = SAMPLE_SECTION_HTML[qid]
            soup = BeautifulSoup(html, "html.parser")
            h1 = soup.find("h1")
            assert scraper._is_tf(h1) is True

    def test_is_tf_four_choice(self):
        """
        Test that _is_tf returns False for four-choice questions.

        Uses SAMPLE_SECTION_HTML for four-choice questions to verify that the
        method returns False.
        """
        scraper = QuestionScraper(IMG_SAVE_PATH, CONFIG_PATH, LOGGER)
        for qid in ["d548b", "10d89"]:
            html = SAMPLE_SECTION_HTML[qid]
            soup = BeautifulSoup(html, "html.parser")
            h1 = soup.find("h1")
            assert scraper._is_tf(h1) is False

class TestExtract4C:
    """Unit tests for the _extract_4c method of QuestionScraper, which extracts
    four-choice options as a dictionary."""

    def test_extract_4c(self):
        """
        Test that _extract_4c returns a dictionary mapping letters to answers.

        Uses SAMPLE_SECTION_HTML for four-choice questions to verify that the
        returned dictionary maps option letters (A-D) to their corresponding answers.
        """
        scraper = QuestionScraper(IMG_SAVE_PATH, CONFIG_PATH, LOGGER)
        expected_dicts = {
            "d548b": {
                "A": "拦截过往车辆帮助拖车",
                "B": "借用其他机动车牵引",
                "C": "车上人员应当坐在车内等待救援",
                "D": "开启危险报警闪光灯，并在来车方向150米外设置警告标志"
            },
            "10d89": {
                "A": "让左方道路车辆先行",
                "B": "让右方道路车辆先行",
                "C": "直接加速直行通过",
                "D": "开启危险报警闪光灯通行"
            }
        }
        for qid in ["d548b", "10d89"]:
            html = SAMPLE_SECTION_HTML[qid]
            soup = BeautifulSoup(html, "html.parser")
            h1 = soup.find("h1")
            d = scraper._extract_4c(h1)
            assert d == expected_dicts[qid]

class TestGetAns:
    """Unit tests for the _get_ans method of QuestionScraper, which returns the
    correct answer for a question."""

    def test_get_ans_true_false(self):
        """
        Test that _get_ans returns the correct answer for true/false questions.

        Uses SAMPLE_SECTION_HTML for true/false questions to verify that the
        correct answer ("对" or "错") is returned.
        """
        scraper = QuestionScraper(IMG_SAVE_PATH, CONFIG_PATH, LOGGER)
        expected = {
            "b37fe": "错",
            "89195": "对"
        }
        for qid in ["b37fe", "89195"]:
            html = SAMPLE_SECTION_HTML[qid]
            soup = BeautifulSoup(html, "html.parser")
            h1 = soup.find("h1")
            ans = scraper._get_ans(h1)
            assert ans == expected[qid]

    def test_get_ans_four_choice(self):
        """
        Test that _get_ans returns the correct answer for four-choice questions.

        Uses SAMPLE_SECTION_HTML for four-choice questions to verify that the
        correct answer text is returned based on the marked option.
        """
        scraper = QuestionScraper(IMG_SAVE_PATH, CONFIG_PATH, LOGGER)
        expected = {
            "d548b": "开启危险报警闪光灯，并在来车方向150米外设置警告标志",
            "10d89": "让右方道路车辆先行"
        }
        for qid in ["d548b", "10d89"]:
            html = SAMPLE_SECTION_HTML[qid]
            soup = BeautifulSoup(html, "html.parser")
            h1 = soup.find("h1")
            ans = scraper._get_ans(h1)
            assert ans == expected[qid]
