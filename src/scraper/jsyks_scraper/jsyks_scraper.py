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
        self.qid_scraper.connect()
        self.question_scraper = QuestionScraper(qb.get_img_dir(),
                                                Q_SCRAPER_CONFIG_PATH,
                                                logger)

    def fill_question_bank(self) -> None:
        """
        Scrapes question IDs and then scrapes questions using those IDs.
        Fills the question bank with the scraped questions.
        """
        self.logger.info("Starting to scrape question IDs")
        # Get chapters and their question IDs
        chapters = self.qid_scraper.get_chapters()

        # Add chapters to question bank
        for chapter_num, (chapter_desc, qids) in chapters.items():
            self.logger.info(f"Adding chapter {chapter_num}: {chapter_desc} "
                             f"with {len(qids)} questions")
            self.qb.add_chapter(chapter_num, chapter_desc)

            # Scrape each question and add to question bank
            for qid in qids:
                self.logger.debug(f"Scraping question {qid}")
                try:
                    question = self.question_scraper.get_question(qid)
                    if question:
                        self.qb.add_question(question, chapter_num)
                except Exception as e:
                    self.logger.error(f"Error scraping question {qid}: {e}")

            self.logger.info(f"Completed chapter {chapter_num} with "
                             f"{self.qb.question_count(chapter_num)} questions")
