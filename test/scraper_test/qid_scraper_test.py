# Tests for the qid scraper

# Library Imports
import pytest
import json

from PIL.ImageOps import scale
from bs4 import BeautifulSoup
import logging
import os

# Local Imports
from scraper.jsyks_scraper._qid_scraper import QidScraper


# ========== Constants for Testing ==========
TEST_CONFIG_PATH = "scraper_test/qid_test_config.json"
TEST_MATERIAL_PATH = "scraper_test/qid_test_material.json"

# Load test material from the JSON file
with open(TEST_MATERIAL_PATH, "r") as file:
    TEST_MATERIAL = json.load(file)

# Constants for testing
SAMPLE_MENU_SECTION = BeautifulSoup(TEST_MATERIAL["SAMPLE_MENU_SECTION"],
                                    "html.parser")
SAMPLE_PAGE_BAR_WITH_LAST_PAGE = BeautifulSoup(
    TEST_MATERIAL["SAMPLE_PAGE_BARS"]["has last page button"],
    "html.parser")
SAMPLE_PAGE_BAR_WITHOUT_LAST_PAGE = BeautifulSoup(
    TEST_MATERIAL["SAMPLE_PAGE_BARS"]["no last page button"],
    "html.parser")

# Convert string keys to int keys to match QidScraper's attribute types
CHAPTERS = {int(k): v for k, v in TEST_MATERIAL["CHAPTERS"].items()}
CHAPTER_TO_CHAPTER_URL = {int(k): v for k, v in
                          TEST_MATERIAL["CHAPTER_TO_CHAPTER_URL"].items()}
CHAPTER_TO_PAGE_COUNT = {int(k): v for k, v in
                         TEST_MATERIAL["CHAPTER_TO_PAGE_COUNT"].items()}
SAMPLE_QLIST_URL = TEST_MATERIAL["SAMPLE_QLIST_URL"]
SAMPLE_QUESTION_LIST = BeautifulSoup(
    TEST_MATERIAL["SAMPLE_QUESTION_LIST"],
    "html.parser")
SAMPLE_QLIST_QID = set(TEST_MATERIAL["SAMPLE_QLIST_QID"])

# Generate sample chapter to URLs mapping
SAMPLE_CHAPT_TO_URLS = {}
base_url = "https://tiba.jsyks.com/kmytk"
for chapter_num, url in CHAPTER_TO_CHAPTER_URL.items():
    SAMPLE_CHAPT_TO_URLS[chapter_num] = []
    # Extract chapter code from URL (e.g., "https://tiba.jsyks.com/kmytk_1501" -> "1501")
    chapter_code = url.split('_')[1]
    # Generate URLs for all pages in the chapter
    for i in range(1, CHAPTER_TO_PAGE_COUNT[chapter_num] + 1):
        SAMPLE_CHAPT_TO_URLS[chapter_num].append(f"{base_url}_{chapter_code}_{i}")

# ========== Logger =========
def setup_test_logger(name="qid_scraper_test"):
    """
    Set up a verbose logger for testing that logs to the test_logs directory.

    Args:
        name (str): Name of the logger

    Returns:
        logging.Logger: Configured logger instance
    """
    log_file = os.path.join("test_logs", f"{name}.log")

    logger = logging.getLogger(name)
    # Set to debug level for verbose logging
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Less verbose for console

    # Create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info(f"Test logger initialized. Logging to {log_file}")
    return logger

# Create the test logger
TEST_LOGGER = setup_test_logger()

# ========== Tests ==========
class TestQidScraperInit:
    """Tests for QidScraper initialization"""

    def test_init_loads_config_correctly(self):
        """Test that the initializer correctly loads configuration from the
        provided JSON file.

        Uses: TEST_CONFIG_PATH for initialization
              Verifies private attributes match expected values from config
        """
        # Create a QidScraper instance
        scraper = QidScraper(TEST_LOGGER, TEST_CONFIG_PATH)

        with open(TEST_CONFIG_PATH, "r") as file:
            config = json.load(file)
        # Check if private attributes are set correctly from the config
        assert scraper._base_url == config["base_url"]
        assert scraper._clst_cid == config["c_lst_cls_name"]
        assert scraper._pb_cid == config["page_bar_cls_name"]
        assert scraper._qlst_cid == config["q_lst_cls_name"]

    def test_init_creates_empty_data_structures(self):
        """Test that the initializer correctly sets up empty data structures
        for chapters, chapter URLs, etc.

        Uses: TEST_CONFIG_PATH for initialization
              Verifies _chapters, _chapt_to_chapturl, and _chapt_to_urls are
              empty
        """
        # Create a QidScraper instance
        scraper = QidScraper(TEST_LOGGER, TEST_CONFIG_PATH)

        # Check that the data structures are empty
        assert scraper._chapters == {}
        assert scraper._chapt_to_chapturl == {}
        assert scraper._chapt_to_urls == {}

    def test_init_assigns_logger(self):
        """Test that the initializer correctly assigns the provided logger.

        Uses: TEST_LOGGER for initialization
              Verifies _logger attribute is set correctly
        """
        # Create a QidScraper instance
        scraper = QidScraper(TEST_LOGGER, TEST_CONFIG_PATH)

        # Check if the logger is assigned correctly
        assert scraper._logger == TEST_LOGGER


class TestQidScraperConnect:
    """Tests for QidScraper.connect method"""

    def test_connect_populates_chapters_dict(self):
        """Test that connect() correctly populates the _chapters dictionary.

        Uses: TEST_CONFIG_PATH for initialization
              CHAPTERS as expected output for _chapters
        """
        scraper = QidScraper(TEST_LOGGER, TEST_CONFIG_PATH)
        assert scraper._chapters == {}
        scraper.connect()
        assert scraper._chapters == CHAPTERS

        # Check specific values to make sure the content is correct
        for chapter_num, chapter_name in CHAPTERS.items():
            assert scraper._chapters[chapter_num] == chapter_name

        TEST_LOGGER.info("connect() correctly populated the _chapters dictionary")

    def test_connect_populates_chapter_url_dict(self):
        """Test that connect() correctly populates the _chapt_to_chapturl dictionary.

        Uses: TEST_CONFIG_PATH for initialization
              CHAPTER_TO_CHAPTER_URL as expected output for _chapt_to_chapturl
        """
        scraper = QidScraper(TEST_LOGGER, TEST_CONFIG_PATH)
        assert scraper._chapt_to_chapturl == {}
        scraper.connect()
        assert scraper._chapt_to_chapturl == CHAPTER_TO_CHAPTER_URL

    def test_connect_populates_urls_dict(self):
        """Test that connect() correctly populates the _chapt_to_urls dictionary.

        Uses: TEST_CONFIG_PATH for initialization
              SAMPLE_CHAPT_TO_URLS as expected output for _chapt_to_urls
        """
        scraper = QidScraper(TEST_LOGGER, TEST_CONFIG_PATH)
        assert scraper._chapt_to_urls == {}
        scraper.connect()
        assert scraper._chapt_to_urls == SAMPLE_CHAPT_TO_URLS

    def test_connect_end_to_end(self):
        """Test the end-to-end functionality of connect().

        Uses: TEST_CONFIG_PATH for initialization
              No mocking - tests actual connection to site
              Verifies all data structures are populated correctly

        Note: This test makes actual network requests and may be slow or fail
              if the website is unavailable.
        """
        scraper = QidScraper(TEST_LOGGER, TEST_CONFIG_PATH)
        scraper.connect()

        # Verify the number of chapters matches the expected count
        assert scraper._chapters == CHAPTERS
        TEST_LOGGER.debug(f"Chapters retrieved")
        assert scraper._chapt_to_chapturl == CHAPTER_TO_CHAPTER_URL
        TEST_LOGGER.debug(f"Chapter URLs retrieved")
        assert scraper._chapt_to_urls == SAMPLE_CHAPT_TO_URLS
        TEST_LOGGER.debug(f"Full URLs retrieved")

class TestExtractChapterSection:
    """Tests for QidScraper._extract_chapter_section"""

    def test_extract_chapter_section_returns_correct_soup(self):
        """Test that _extract_chapter_section returns the correct BeautifulSoup
        object.

        Uses: SAMPLE_MENU_SECTION as expected return value

        Note: Makes an actual request to an external site.
        """
        # Create a QidScraper instance
        scraper = QidScraper(TEST_LOGGER, TEST_CONFIG_PATH)
        print(scraper._base_url)
        result = scraper._extract_chapter_section(scraper._base_url)

        # Verify it's a BeautifulSoup object
        assert isinstance(result, BeautifulSoup)

        # Verify it contains the expected content
        assert result == SAMPLE_MENU_SECTION


class TestExtractChapters:
    """Tests for QidScraper._extract_chapters"""

    def test_extract_chapters_populates_chapters_dict(self):
        """Test that _extract_chapters correctly populates the _chapters
        dictionary.

        Uses: SAMPLE_MENU_SECTION as input
              CHAPTERS as expected output
        """
        scraper = QidScraper(TEST_LOGGER, TEST_CONFIG_PATH)
        scraper._extract_chapters(SAMPLE_MENU_SECTION)
        assert scraper._chapters == CHAPTERS

    def test_extract_chapters_populates_chapter_url_dict(self):
        """Test that _extract_chapters correctly populates the
        _chapt_to_chapturl dictionary.

        Uses: SAMPLE_MENU_SECTION as input
              CHAPTER_TO_CHAPTER_URL as expected output
        """
        scraper = QidScraper(TEST_LOGGER, TEST_CONFIG_PATH)
        scraper._extract_chapters(SAMPLE_MENU_SECTION)
        assert scraper._chapt_to_chapturl == CHAPTER_TO_CHAPTER_URL


class TestSetUpUrls:
    """Tests for QidScraper._set_up_urls"""

    def test_set_up_urls_populates_urls_dict(self):
        """Test that _set_up_urls correctly populates the _chapt_to_urls
        dictionary.

        Uses: CHAPTER_TO_CHAPTER_URL for request URLs
              SAMPLE_PAGE_BAR_WITH_LAST_PAGE/SAMPLE_PAGE_BAR_WITHOUT_LAST_PAGE
              CHAPTER_TO_PAGE_COUNT to verify URL count

        Note: Involves making multiple requests to external sites if not mocked.
        """
        scraper = QidScraper(TEST_LOGGER, TEST_CONFIG_PATH)
        scraper._extract_chapters(SAMPLE_MENU_SECTION)
        scraper._set_up_urls()
        assert scraper._chapt_to_urls == SAMPLE_CHAPT_TO_URLS


class TestExtractUrls:
    """Tests for QidScraper._extract_urls"""

    def test_extract_urls_with_last_page_button(self):
        """Test that _extract_urls correctly extracts URLs when a last page
        button is present.

        Uses: SAMPLE_PAGE_BAR_WITH_LAST_PAGE as input
              CHAPTER_TO_PAGE_COUNT for verification
        """
        # Create a QidScraper instance
        scraper = QidScraper(TEST_LOGGER, TEST_CONFIG_PATH)

        # Initialize the _chapt_to_urls dictionary for chapter 2
        chapter_num = 2
        scraper._chapt_to_urls = {chapter_num: []}

        # Call the method with the sample page bar
        scraper._extract_urls(SAMPLE_PAGE_BAR_WITH_LAST_PAGE, chapter_num)

        # Verify that the correct number of URLs was generated
        expected_page_count = CHAPTER_TO_PAGE_COUNT[chapter_num]
        TEST_LOGGER.debug(f"Expected page count for chapter {chapter_num}: {expected_page_count}")
        TEST_LOGGER.debug(f"Actual URL count: {len(scraper._chapt_to_urls[chapter_num])}")

        assert len(scraper._chapt_to_urls[chapter_num]) == expected_page_count

        # Verify that URLs have the correct format
        chapter_code = "1502"  # From the sample data
        for i, url in enumerate(scraper._chapt_to_urls[chapter_num], 1):
            expected_url = f"{scraper._base_url}_{chapter_code}_{i}"
            TEST_LOGGER.debug(f"Expected URL: {expected_url}")
            TEST_LOGGER.debug(f"Actual URL: {url}")
            assert url == expected_url

        TEST_LOGGER.info("_extract_urls correctly extracted URLs with last page button")

    def test_extract_urls_without_last_page_button(self):
        """Test that _extract_urls correctly extracts URLs when no last page
        button is present.

        Uses: SAMPLE_PAGE_BAR_WITHOUT_LAST_PAGE as input
              CHAPTER_TO_PAGE_COUNT for verification
        """
        # Create a QidScraper instance
        scraper = QidScraper(TEST_LOGGER, TEST_CONFIG_PATH)

        # Initialize the _chapt_to_urls dictionary for chapter 4
        chapter_num = 4
        scraper._chapt_to_urls = {chapter_num: []}

        # Call the method with the sample page bar
        scraper._extract_urls(SAMPLE_PAGE_BAR_WITHOUT_LAST_PAGE, chapter_num)

        # Verify that the correct number of URLs was generated
        expected_page_count = CHAPTER_TO_PAGE_COUNT[chapter_num]
        TEST_LOGGER.debug(f"Expected page count for chapter {chapter_num}: {expected_page_count}")
        TEST_LOGGER.debug(f"Actual URL count: {len(scraper._chapt_to_urls[chapter_num])}")

        assert len(scraper._chapt_to_urls[chapter_num]) == expected_page_count

        # Verify that URLs have the correct format
        chapter_code = "1504"  # From the sample data
        for i, url in enumerate(scraper._chapt_to_urls[chapter_num], 1):
            expected_url = f"{scraper._base_url}_{chapter_code}_{i}"
            TEST_LOGGER.debug(f"Expected URL: {expected_url}")
            TEST_LOGGER.debug(f"Actual URL: {url}")
            assert url == expected_url

        TEST_LOGGER.info("_extract_urls correctly extracted URLs without last page button")

    def test_extract_urls_generates_correct_page_urls(self):
        """Test that _extract_urls generates the correct page URLs for a
        chapter.

        Uses: SAMPLE_PAGE_BAR_WITH_LAST_PAGE or SAMPLE_PAGE_BAR_WITHOUT_LAST_PAGE
              Verifies URL format matches expected pattern
        """
        # Create a QidScraper instance
        scraper = QidScraper(TEST_LOGGER, TEST_CONFIG_PATH)

        # Test with both types of page bars
        test_data = [
            (SAMPLE_PAGE_BAR_WITH_LAST_PAGE, 2, "1502"),
            (SAMPLE_PAGE_BAR_WITHOUT_LAST_PAGE, 4, "1504")
        ]

        for page_bar, chapter_num, chapter_code in test_data:
            # Initialize the _chapt_to_urls dictionary for the chapter
            scraper._chapt_to_urls = {chapter_num: []}

            # Call the method with the sample page bar
            scraper._extract_urls(page_bar, chapter_num)

            # Verify URL format
            for i, url in enumerate(scraper._chapt_to_urls[chapter_num], 1):
                # URLs should follow the pattern: base_url_chapterCode_pageNumber
                assert url.startswith(f"{scraper._base_url}_{chapter_code}_")

                # Extract the page number from the URL and verify it matches the index
                page_num = int(url.split('_')[-1])
                assert page_num == i

                # The chapter code should be in the URL
                assert chapter_code in url

            TEST_LOGGER.info(f"_extract_urls generated correct page URLs for chapter {chapter_num}")


class TestGetChapters:
    """Tests for QidScraper.get_chapters"""

    def test_get_chapters_returns_correct_dict(self):
        """Test that get_chapters returns the correct dictionary of
        chapters.

        Uses: CHAPTERS as expected output
        """
        # Create a QidScraper instance
        scraper = QidScraper(TEST_LOGGER, TEST_CONFIG_PATH)
        scraper.connect()
        result = scraper.get_chapters()
        assert result == CHAPTERS


class TestGetChapterToQids:
    """Tests for QidScraper.get_chapter_to_qids"""

    @pytest.fixture(autouse=True)
    def setup(self):
        scraper = QidScraper(TEST_LOGGER, TEST_CONFIG_PATH)
        scraper.connect()
        self.result = scraper.get_chapter_to_qids()

    def test_get_chapter_to_qids_size(self):
        """Test that get_chapter_to_qids returns the correct mapping of
        chapters to qids.
        """
        assert len(self.result) == len(CHAPTERS)

    def test_chapter_one_qid_size(self):
        """ Test that get_chapter_to_qids returns the correct number of QIDs
        for Chapter 1 """
        # There are 717 questions in Chapter 1
        assert len(self.result[1]) == 717


class TestGetQidSection:
    """Tests for QidScraper._get_qid_section"""

    def test_get_qid_section_returns_correct_soup(self):
        """Test that _get_qid_section returns the correct BeautifulSoup
        object.

        Uses: SAMPLE_QUESTION_LIST as expected return value
        """
        # Create a QidScraper instance
        scraper = QidScraper(TEST_LOGGER, TEST_CONFIG_PATH)
        result = scraper._get_qid_section(SAMPLE_QLIST_URL)
        assert isinstance(result, BeautifulSoup)
        assert result == SAMPLE_QUESTION_LIST


class TestExtractQid:
    """Tests for QidScraper._extract_qid"""

    def test_extract_qid_returns_correct_qids(self):
        """Test that _extract_qid correctly extracts qids from a BeautifulSoup
        section.

        Uses: SAMPLE_QUESTION_LIST as input
              SAMPLE_QLIST_QID as expected output
        """
        scraper = QidScraper(TEST_LOGGER, TEST_CONFIG_PATH)
        result = scraper._extract_qid(SAMPLE_QUESTION_LIST)
        assert result == set(SAMPLE_QLIST_QID)
