# Data class for a question
from abc import ABC, abstractmethod
from typing import Set, Any

class Question(ABC):
    """
    Interface for a question.
    """
    _qid: str
    _question: str
    _image_url: Any(str, None)
    _answers: Set[str]
    _correct_answer: str

    def __init__(self, qid: str, question: str, answers: Set[str],
                 correct_answer: str, image_url: Any(str, None) = None):
        """
        Initializes the Question with the provided parameters.

        :param qid: Unique identifier for the question.
        :param question: The text of the question.
        :param answers: Set of possible answers.
        :param correct_answer: The correct answer to the question.
        """
        self._qid = qid
        self._question = question
        self._answers = answers
        self._correct_answer = correct_answer
        self._image_url = image_url
        self.check_format()

    @abstractmethod
    def check_format(self):
        """ Check if the question format is correct and raise an error if not.
        """
        raise NotImplementedError

class FourChoiceText(Question):
    """
    Data class for a question with choices A, B, C, D with no image.
    """

    def check_format(self):
        """
        Checks if the question format is correct.
        Raises IncorrectFormatError if the format is incorrect.
        """
        if len(self._answers) != 4:
            raise IncorrectFormatError("FourChoiceQ must have exactly 4 answers.")
        if self._correct_answer not in self._answers:
            raise IncorrectFormatError("Correct answer must be one of the provided answers.")
        if self._image_url is not None:
            raise IncorrectFormatError("FourChoiceQ should not have an image URL.")

class TwoChoiceText(Question):
    """
    Data class for a question with choices A, B with no image.
    """
    def check_format(self):
        """
        Checks if the question format is correct.
        Raises IncorrectFormatError if the format is incorrect.
        """
        if len(self._answers) != 2:
            raise IncorrectFormatError("TwoChoiceQ must have exactly 2 answers.")
        if self._correct_answer not in self._answers:
            raise IncorrectFormatError("Correct answer must be one of the provided answers.")

class FourChoiceImage(Question):
    """
    Data class for a question with choices A, B, C, D with an image.
    """

    def check_format(self):
        """
        Checks if the question format is correct.
        Raises IncorrectFormatError if the format is incorrect.
        """
        if len(self._answers) != 4:
            raise IncorrectFormatError("FourChoiceImage must have exactly 4 answers.")
        if self._correct_answer not in self._answers:
            raise IncorrectFormatError("Correct answer must be one of the provided answers.")
        if self._image_url is None:
            raise IncorrectFormatError("FourChoiceImage must have an image URL.")


class TwoChoiceImage(Question):
    """
    Data class for a question with choices A, B with an image.
    """
    def check_format(self):
        """
        Checks if the question format is correct.
        Raises IncorrectFormatError if the format is incorrect.
        """
        if len(self._answers) != 2:
            raise IncorrectFormatError("TwoChoiceImage must have exactly 2 answers.")
        if self._correct_answer not in self._answers:
            raise IncorrectFormatError("Correct answer must be one of the provided answers.")
        if self._image_url is None:
            raise IncorrectFormatError("TwoChoiceImage must have an image URL.")


class IncorrectFormatError(TypeError):
    """ Error class for incorrect question format. """

    def __init__(self, message: str):
        """
        Initializes the IncorrectFormatError with a message.
        """
        super().__init__(message)
