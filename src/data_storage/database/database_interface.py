# Public interface for the database module
from abc import ABC, abstractmethod

from data_storage.in_memory.question_bank import QuestionBank


class Database(ABC):
    """
    A database for storing the questionbank
    """

    @abstractmethod
    def save(self, qb: QuestionBank) -> bool:
        """
        Save the question bank to the database.
        :param qb:
        :return: True iff the question bank was saved successfully
        """
        raise NotImplementedError

    @abstractmethod
    def load(self) -> QuestionBank:
        """
        Load a question bank from the database.
        :return: The question bank stored in the database.
        """
        raise NotImplementedError
