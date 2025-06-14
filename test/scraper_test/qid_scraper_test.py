# Tests for the qid scraper

# Library Imports
import pytest

# Local Imports
from scraper.jsyks_scraper._qid_scraper import QidScraper

TEST_CONFIG_PATH = "scraper_test/site_info_test.json"
SAMPLE_URL = "https://tiba.jsyks.com/kmytk_1502_2"

class TestInit:
    pass

class TestGetQidSection:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.scraper = QidScraper(TEST_CONFIG_PATH)

    def test_get_qid_section(self):
        section = self.scraper._get_qid_section(SAMPLE_URL)
        assert section is not None, "Section should not be None"

class TestExtractQid:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.scraper = QidScraper(TEST_CONFIG_PATH)
        self.section = self.scraper._get_qid_section(SAMPLE_URL)

    def test_extract_qid_format(self):
        qids = self.scraper._extract_qid(self.section)
        assert isinstance(qids, list), "Extracted QIDs should be a list"
        assert len(qids) > 0, "Extracted QIDs list should not be empty"
        for qid in qids:
            assert isinstance(qid, str), "Each QID should be a string"

    def test_extract_qid_start_end(self):
        qids = self.scraper._extract_qid(self.section)
        assert qids[0] == "9e042"
        assert qids[-1] == "e3643"
