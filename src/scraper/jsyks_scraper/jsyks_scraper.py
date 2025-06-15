# Basic implementation of the scraper interface by first retrieving the
# question ids and then scraping the questions using those ids.
from logging import Logger

# Local Imports
from scraper.scraper_interface import Scraper
from scraper.jsyks_scraper._qid_scraper import QidScraper
from scraper.jsyks_scraper._question_scraper import QuestionScraper
from data_storage.in_memory.question_bank import QuestionBank

class JSYKSScraper(Scraper):
    """
    Scraper that scrapes questions from the JSYKS website.

    It first retrieves question IDs and then scrapes the questions using those
    IDs.
    """

    def __init__(self, qb: QuestionBank, logger: Logger, config_path: str):
        """
        Initializes the JSYKSScraper with a QuestionBank and a Logger.

        Args:
            qb (QuestionBank): The question bank to store scraped questions.
            logger (Logger): The logger to log messages.
        """
        self.qid_scraper = QidScraper(logger, config_path)
        self.question_scraper = QuestionScraper(qb.get_img_dir(), config_path,
                                                logger)

    def fill_question_bank(self) -> None:
        pass
