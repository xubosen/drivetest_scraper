# Public interface for the scrapers
from abc import ABC, abstractmethod
from logging import Logger

from questions.question_bank import QuestionBank

class Scraper(ABC):
    """
    Abstract base class for scrapers.
    """
    @abstractmethod
    def __init__(self, qb: QuestionBank, logger: Logger):
        """
        Initializes the scraper with a question bank and a logger.

        Args:
            qb (QuestionBank): The question bank to use.
            logger (Logger): The logger to use for logging.
        """
        raise NotImplementedError

    @abstractmethod
    def fill_question_bank(self) -> None:
        """
        Abstract method to fill the question bank.
        """
        raise NotImplementedError
