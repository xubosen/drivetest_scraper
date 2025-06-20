# Basic implementation of the scraper interface by first retrieving the
# question ids and then scraping the questions using those ids.
from logging import Logger

# Local Imports
from scraper.scraper_interface import Scraper
from scraper.jsyks_scraper._qid_scraper import QidScraper
from scraper.jsyks_scraper._question_scraper import QuestionScraper
from data_storage.in_memory.question_bank import QuestionBank

QID_SCRAPER_CONFIG_PATH = "scraper/jsyks_scraper/id_site_info.json"
Q_SCRAPER_CONFIG_PATH = "scraper/jsyks_scraper/q_site_info.json"

class JSYKSScraper(Scraper):
    """
    Scraper that scrapes questions from the JSYKS website.

    It first retrieves question IDs and then scrapes the questions using those
    IDs.
    """

    def __init__(self, qb: QuestionBank, logger: Logger):
        """
        Initializes the JSYKSScraper with a QuestionBank and a Logger.

        Args:
            qb (QuestionBank): The question bank to store scraped questions.
            logger (Logger): The logger to log messages.
        """
        self.qb = qb
        self.logger = logger
        self.qid_scraper = QidScraper(logger, QID_SCRAPER_CONFIG_PATH)
        self.question_scraper = QuestionScraper(qb.get_img_dir(),
                                                Q_SCRAPER_CONFIG_PATH,
                                                logger)

    def fill_question_bank(self) -> None:
        """
        Scrapes question IDs and then scrapes questions using those IDs.
        Fills the question bank with the scraped questions.
        """
        # Get chapters and their question IDs
        self.logger.info("Starting to scrape question IDs")
        self.qid_scraper.connect()
        chapters = self.qid_scraper.get_chapters()
        chapter_to_q_ids = self.qid_scraper.get_chapter_to_qids()

        for chapter in chapters.keys():
            # Add chapter to the question bank
            self.logger.info(f"Adding chapter {chapter} to the question bank")
            self.qb.add_chapter(chapter, chapters[chapter])

            # Scrape questions by id and add them to the question bank
            self.logger.info(f"Scraping questions for chapter {chapter}")
            for qid in chapter_to_q_ids[chapter]:
                self.logger.info(f"Scraping question with ID {qid}")
                question = self.question_scraper.get_question(qid)
                self.qb.add_question(question, chapter)
