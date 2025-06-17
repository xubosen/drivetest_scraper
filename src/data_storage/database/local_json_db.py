# Database that stores text data in a local JSON file and image data in a local
# directory with addresses stored in the aforementioned JSON file

import json
import os
import shutil
from typing import Dict, Any

from data_storage.database.database_interface import Database
from data_storage.in_memory.question_bank import QuestionBank
from data_storage.in_memory.question import Question


class LocalJsonDB(Database):
    """
    A database for storing the question bank in a local JSON file.
    """
    _db_file_path: str
    _img_dir: str

    def __init__(self, db_file_path: str, img_dir: str):
        """
        Initialize the LocalJsonDB with paths for JSON file and image directory.
        """
        self._db_file_path = db_file_path
        self._img_dir = img_dir

    def save(self, qb: QuestionBank) -> bool:
        """
        Save the question bank to the database.

        :param qb: QuestionBank to save
        :return: True if save was successful, False otherwise
        """
        try:
            # Convert QuestionBank to serializable format
            data = self._serialize_question_bank(qb)

            # Copy images to the image directory
            self._copy_images(qb)

            # Write to JSON file
            with open(self._db_file_path, 'w') as f:
                json.dump(data, f, indent=4)

            return True

        except Exception as e:
            print(f"Error saving question bank: {e}")
            return False

    def load(self) -> QuestionBank:
        """
        Load a question bank from the database.

        :return: The question bank stored in the database
        :raises FileNotFoundError: If the database file doesn't exist
        """
        if not os.path.exists(self._db_file_path):
            raise FileNotFoundError(f"Database file not found: "
                                    f"{self._db_file_path}")

        try:
            # Read JSON file
            with open(self._db_file_path, 'r') as f:
                data = json.load(f)

            # Convert from serialized format to QuestionBank
            return self._deserialize_question_bank(data)
        except Exception as e:
            raise RuntimeError(f"Error loading question bank: {e}")

    def _serialize_question_bank(self, qb: QuestionBank) -> Dict[str, Any]:
        """
        Convert a QuestionBank to a JSON-serializable dictionary.

        :param qb: QuestionBank to serialize
        :return: Dictionary representation of the QuestionBank
        """
        # Get all chapter numbers and question IDs
        chapters = {}
        chap_to_qids = {}
        questions = {}
        for chap_num in qb.get_all_chapter_num():
            chapters[str(chap_num)] = qb.describe_chapter(chap_num)
            qids = qb.get_qids_by_chapter(chap_num)
            chap_to_qids[str(chap_num)] = list(qids)

            # Serialize each question
            for qid in qids:
                question = qb.get_question(qid)
                q_data = {
                    "qid": question.get_qid(),
                    "question": question.get_question(),
                    "answers": list(question.get_answers()),
                    "correct_answer": question.get_correct_answer(),
                    "img_path": self._make_img_path(question)
                }
                questions[qid] = q_data
        result = {"chapters": chapters,
                  "chap_to_qids": chap_to_qids,
                  "questions": questions,
                  "img_dir": self._img_dir
                  }
        return result

    def _make_img_path(self, question):
        return self._img_dir + question.get_qid()

    def _deserialize_question_bank(self, data: Dict[str, Any]) -> QuestionBank:
        """
        Convert a serialized dictionary back to a QuestionBank.

        :param data: Dictionary containing serialized QuestionBank data
        :return: Reconstructed QuestionBank
        """
        # Create a new QuestionBank
        qb = QuestionBank(self._img_dir)

        # If the database is empty, return an empty QuestionBank
        if not data.get("chapters"):
            return qb

        # Add chapters
        for chap_num_str, description in data["chapters"].items():
            chap_num = int(chap_num_str)
            qb.add_chapter(chap_num, description)

        # Add questions
        for qid, q_data in data["questions"].items():
            # Find which chapter this question belongs to
            chapter_num = None
            for chap_num_str, qids in data["chap_to_qids"].items():
                if qid in qids:
                    chapter_num = int(chap_num_str)
                    break

            if chapter_num is not None:
                # Create Question object
                question = Question(
                    qid=q_data["qid"],
                    question=q_data["question"],
                    answers=set(q_data["answers"]),
                    correct_answer=q_data["correct_answer"],
                    img_path=q_data["img_path"]
                )

                # Add to QuestionBank
                qb.add_question(question, chapter_num)
        return qb

    def _copy_images(self, qb: QuestionBank) -> None:
        """
        Copy images from the QuestionBank's image directory to the database
        image directory.

        :param qb: QuestionBank containing images to copy
        """
        # Get all chapter numbers
        for chap_num in qb.get_all_chapter_num():
            # Get all question IDs in this chapter
            q_ids = qb.get_qids_by_chapter(chap_num)

            # Process each question
            for q_id in q_ids:
                question = qb.get_question(q_id)
                cur_path = question.get_img_path()
                new_path = self._make_img_path(question)

                if cur_path and os.path.exists(cur_path):
                    # Copy the image to our database image directory
                    shutil.copy2(cur_path, new_path)
