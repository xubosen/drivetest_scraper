from abc import ABC, abstractmethod

from data_storage.in_memory.question import Question

class QuestionDisplayer(ABC):
    """
    Abstract base class for displaying questions.
    """

    @abstractmethod
    def display_question(self, question: Question) -> None:
        """
        Display the question to the user.

        :param question: The question to be displayed.
        """
        pass

    @abstractmethod
    def display_answer(self, question: Question) -> None:
        """
        Display the answer to the user.

        :param question: The question object containing the answer.
        """
        pass
