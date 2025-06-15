from typing import Dict, Set, List

from questions.question import Question

class QuestionBank:
    """
    A class to manage a collection of questions.
    """
    _ids: Set[str]
    _chapters: Dict[int, str]
    _chap_num_to_ids: Dict[int, Set[str]]
    _id_to_q: Dict[str, Question]
    _img_dir: str

    def __init__(self, img_dir: str):
        """
        Initialize a new QuestionBank.

        :param img_dir: Directory path where question images are stored
        """
        self._ids = set()
        self._chapters = {}
        self._chap_num_to_ids = {}
        self._id_to_q = {}
        self._img_dir = img_dir

    def add_chapter(self, chapter_num: int, description: str):
        """
        Add a new chapter to the question bank.

        :param chapter_num: Unique identifier for the chapter
        :param description: Description of the chapter content
        :raises ValueError: If the chapter number already exists
        """
        if chapter_num not in self._chapters:
            self._chapters[chapter_num] = description
            self._chap_num_to_ids[chapter_num] = set()
        else:
            raise ValueError(f"Chapter {chapter_num} already exists")

    def add_question(self, question: Question, chapter_num: int):
        """
        Add a question to the question bank and associate it with a chapter.

        :param question: The Question to add
        :param chapter_num: The chapter number to associate with this question
        :raises KeyError: If the chapter number does not exist
        """
        self._ids.add(question.get_qid())
        self._chap_num_to_ids[chapter_num].add(question.get_qid())
        self._id_to_q[question.get_qid()] = question

    def get_question(self, q_id: str) -> Question:
        """
        Retrieve a question by its ID.

        :param q_id: The ID of the question to retrieve
        :return: The Question object
        :raises LookupError: If the question ID is not found
        """
        if q_id in self._ids:
            return self._id_to_q[q_id]
        else:
            raise LookupError(f"Question {q_id} not found")

    def get_qids_by_chapter(self, chap_num: int) -> Set[str]:
        """
        Get all question IDs associated with a specific chapter.

        :param chap_num: The chapter number
        :return: A set of question IDs
        :raises LookupError: If the chapter number is not found
        """
        if chap_num in self._chapters.keys():
            return self._chap_num_to_ids[chap_num]
        else:
            raise LookupError(f"Chapter {chap_num} not found")

    def describe_chapter(self, chap_num: int) -> str:
        """
        Get the description of a chapter.

        :param chap_num: The chapter number
        :return: The chapter description
        :raises LookupError: If the chapter number is not found
        """
        if chap_num in self._chapters.keys():
            return self._chapters[chap_num]
        else:
            raise LookupError(f"Chapter {chap_num} not found")

    def get_img_dir(self) -> str:
        """
        Get the directory path where question images are stored.

        :return: Path to the image directory
        """
        return self._img_dir

    def get_all_chapter_num(self) -> List[int]:
        """
        Return an ordered list of chapter numbers
        :return: An ordered list of chapter numbers
        """
        return sorted(self._chapters.keys())

    def question_count(self, chapter_num: int = None) -> int:
        """
        Count the number of questions.

        :param chapter_num: Optional chapter to count questions from
        :return: Number of questions
        """
        if chapter_num is None:
            return len(self._ids)
        else:
            return len(self._chap_num_to_ids[chapter_num])
