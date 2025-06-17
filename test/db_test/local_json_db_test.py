import os
import json
import shutil
from unittest.mock import patch, mock_open

from data_storage.database.local_json_db import LocalJsonDB
from data_storage.in_memory.question_bank import QuestionBank
from data_storage.in_memory.question import Question

SOURCE_IMG_TEST = "db_test/source_img"

TEST_DB_PATH = "db_test/mock_db/data.json"
TEST_IMG_DIR = "db_test/mock_db/images"


def teardown():
    """Clean up the test environment after each test method."""
    # Remove test files and directories
    if os.path.exists(TEST_DB_PATH):
        with open(TEST_DB_PATH, 'w') as f:
            f.write('{}')
    if os.path.exists(TEST_IMG_DIR):
        shutil.rmtree(TEST_IMG_DIR)
        os.makedirs(TEST_IMG_DIR, exist_ok=True)
    if os.path.exists(SOURCE_IMG_TEST):
        shutil.rmtree(SOURCE_IMG_TEST)
        os.makedirs(SOURCE_IMG_TEST, exist_ok=True)

class TestLocalJsonDBInit:
    """Tests for the LocalJsonDB initialization."""

    def test_init_sets_paths(self):
        """Test that init correctly sets the database and image paths."""
        db = LocalJsonDB(TEST_DB_PATH, TEST_IMG_DIR)
        assert db._db_file_path == TEST_DB_PATH
        assert db._img_dir == TEST_IMG_DIR


class TestLocalJsonDBSave:
    """Tests for the save method of LocalJsonDB."""
    def teardown_method(self):
        teardown()

    def test_save_empty_question_bank(self):
        """Test saving an empty question bank."""
        db = LocalJsonDB(TEST_DB_PATH, TEST_IMG_DIR)
        qb = QuestionBank(SOURCE_IMG_TEST)
        result = db.save(qb)
        assert result is True

        # File should exist and contain valid JSON
        assert os.path.exists(TEST_DB_PATH)

        with open(TEST_DB_PATH, 'r') as f:
            data = json.load(f)

        # Check expected structure for empty question bank
        assert "chapters" in data
        assert "chap_to_qids" in data
        assert "questions" in data
        assert "img_dir" in data
        assert data["chapters"] == {}
        assert data["chap_to_qids"] == {}
        assert data["questions"] == {}
        assert data["img_dir"] == TEST_IMG_DIR

    def test_save_question_bank_with_data(self):
        """Test saving a question bank with chapters and questions."""
        db = LocalJsonDB(TEST_DB_PATH, TEST_IMG_DIR)
        qb = QuestionBank(SOURCE_IMG_TEST)

        # Add a chapter
        qb.add_chapter(1, "Test Chapter")

        # Add a question
        question = Question(
            qid="test1",
            question="What is the answer?",
            answers={"A", "B", "C", "D"},
            correct_answer="A"
        )
        qb.add_question(question, 1)

        # Save the question bank
        result = db.save(qb)
        assert result is True

        # Check that file exists
        assert os.path.exists(TEST_DB_PATH)

        # Verify the contents
        with open(TEST_DB_PATH, 'r') as f:
            data = json.load(f)

        assert data["chapters"] == {"1": "Test Chapter"}
        assert data["chap_to_qids"] == {"1": ["test1"]}
        assert "test1" in data["questions"]
        assert data["questions"]["test1"]["question"] == "What is the answer?"
        assert set(data["questions"]["test1"]["answers"]) == {"A", "B", "C", "D"}
        assert data["questions"]["test1"]["correct_answer"] == "A"


class TestLocalJsonDBLoad:
    """Tests for the load method of LocalJsonDB."""
    def teardown_method(self):
        teardown()

    def test_load_empty_file(self):
        """Test loading from an empty database file."""
        db = LocalJsonDB(TEST_DB_PATH, TEST_IMG_DIR)
        # Create an empty file
        with open(TEST_DB_PATH, 'w') as f:
            f.write('{}')

        # Should not raise an error but return an empty QuestionBank
        qb = db.load()
        assert isinstance(qb, QuestionBank)
        assert qb.get_all_chapter_num() == []
        assert qb.question_count() == 0

    def test_load_valid_file(self):
        """Test loading from a valid database file."""
        db = LocalJsonDB(TEST_DB_PATH, TEST_IMG_DIR)
        # Create test data
        test_data = {
            "chapters": {"1": "Test Chapter"},
            "chap_to_qids": {"1": ["test1"]},
            "questions": {
                "test1": {
                    "qid": "test1",
                    "question": "What is the answer?",
                    "answers": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "img_path": TEST_IMG_DIR + "test1"
                }
            },
            "img_dir": TEST_IMG_DIR
        }

        # Write test data to file
        with open(TEST_DB_PATH, 'w') as f:
            json.dump(test_data, f)

        # Load the data
        qb = db.load()

        # Verify the loaded QuestionBank
        assert isinstance(qb, QuestionBank)
        assert qb.get_all_chapter_num() == [1]
        assert qb.describe_chapter(1) == "Test Chapter"
        assert qb.get_qids_by_chapter(1) == {"test1"}

        question = qb.get_question("test1")
        assert question.get_question() == "What is the answer?"
        assert question.get_answers() == {"A", "B", "C", "D"}
        assert question.get_correct_answer() == "A"


class TestSerializeQuestionBank:
    """Tests for the _serialize_question_bank method."""

    def setup_method(self):
        """Set up test environment before each test method."""
        self.db = LocalJsonDB(TEST_DB_PATH, TEST_IMG_DIR)

    def teardown_method(self):
        teardown()

    def test_serialize_empty_question_bank(self):
        """Test serializing an empty question bank."""
        qb = QuestionBank(TEST_IMG_DIR)
        result = self.db._serialize_question_bank(qb)

        assert result["chapters"] == {}
        assert result["chap_to_qids"] == {}
        assert result["questions"] == {}
        assert result["img_dir"] == TEST_IMG_DIR

    def test_serialize_with_chapters_no_questions(self):
        """Test serializing a question bank with chapters but no questions."""
        qb = QuestionBank(TEST_IMG_DIR)
        qb.add_chapter(1, "Chapter 1")
        qb.add_chapter(2, "Chapter 2")

        result = self.db._serialize_question_bank(qb)

        assert result["chapters"] == {"1": "Chapter 1", "2": "Chapter 2"}
        assert result["chap_to_qids"] == {"1": [], "2": []}
        assert result["questions"] == {}

    def test_serialize_with_questions_no_images(self):
        """Test serializing a question bank with questions but no images."""
        qb = QuestionBank(TEST_IMG_DIR)
        qb.add_chapter(1, "Chapter 1")

        question = Question(
            qid="q1",
            question="Test question?",
            answers={"Yes", "No", "Maybe"},
            correct_answer="Yes"
        )
        qb.add_question(question, 1)

        result = self.db._serialize_question_bank(qb)

        assert result["chapters"] == {"1": "Chapter 1"}
        assert result["chap_to_qids"] == {"1": ["q1"]}
        assert "q1" in result["questions"]
        assert result["questions"]["q1"]["question"] == "Test question?"
        assert set(result["questions"]["q1"]["answers"]) == {"Yes", "No", "Maybe"}
        assert result["questions"]["q1"]["correct_answer"] == "Yes"
        assert result["questions"]["q1"]["img_path"] == TEST_IMG_DIR + "q1"

    def test_serialize_with_questions_and_images(self):
        """Test serializing a question bank with questions and images."""
        qb = QuestionBank(TEST_IMG_DIR)
        qb.add_chapter(1, "Chapter 1")

        question = Question(
            qid="q1",
            question="Test question?",
            answers={"Yes", "No", "Maybe"},
            correct_answer="Yes",
            img_path=TEST_IMG_DIR + "test_image.jpg"
        )
        qb.add_question(question, 1)

        result = self.db._serialize_question_bank(qb)

        assert "q1" in result["questions"]
        assert result["questions"]["q1"]["img_path"] == TEST_IMG_DIR + "q1"

    def test_serialize_structure_format(self):
        """Test that the serialized structure has the correct format."""
        qb = QuestionBank(TEST_IMG_DIR)
        qb.add_chapter(1, "Chapter 1")

        question = Question(
            qid="q1",
            question="Test question?",
            answers={"Yes", "No", "Maybe"},
            correct_answer="Yes"
        )
        qb.add_question(question, 1)

        result = self.db._serialize_question_bank(qb)

        # Check top level structure
        assert set(result.keys()) == {"chapters", "chap_to_qids", "questions", "img_dir"}

        # Check nested structure
        assert isinstance(result["chapters"], dict)
        assert isinstance(result["chap_to_qids"], dict)
        assert isinstance(result["questions"], dict)
        assert isinstance(result["img_dir"], str)

        # Check question structure
        q_data = result["questions"]["q1"]
        assert set(q_data.keys()) == {"qid", "question", "answers", "correct_answer", "img_path"}
        assert isinstance(q_data["answers"], list)


class TestMakeImgPath:
    """Tests for the _make_img_path method."""

    def setup_method(self):
        self.db = LocalJsonDB(TEST_DB_PATH, TEST_IMG_DIR)

    def teardown_method(self):
        teardown()

    def test_make_img_path_format(self):
        """Test that the image path is correctly formatted."""
        question = Question(
            qid="test123",
            question="Test?",
            answers={"A", "B"},
            correct_answer="A"
        )

        path = self.db._make_img_path(question)
        expected_path = TEST_IMG_DIR + "test123"
        assert path == expected_path

    def test_make_img_path_with_different_directories(self):
        """Test image path creation with different directory settings."""
        custom_img_dir = "/custom/path/"
        db = LocalJsonDB(TEST_DB_PATH, custom_img_dir)

        question = Question(
            qid="test123",
            question="Test?",
            answers={"A", "B"},
            correct_answer="A"
        )

        path = db._make_img_path(question)
        expected_path = custom_img_dir + "test123"
        assert path == expected_path


class TestDeserializeQuestionBank:
    """Tests for the _deserialize_question_bank method."""

    def setup_method(self):
        self.db = LocalJsonDB(TEST_DB_PATH, TEST_IMG_DIR)

    def teardown_method(self):
        teardown()

    def test_deserialize_empty_data(self):
        """Test deserializing empty data."""
        data = {
            "chapters": {},
            "chap_to_qids": {},
            "questions": {},
            "img_dir": TEST_IMG_DIR
        }

        qb = self.db._deserialize_question_bank(data)

        assert isinstance(qb, QuestionBank)
        assert qb.get_all_chapter_num() == []
        assert qb.question_count() == 0

    def test_deserialize_with_chapters_no_questions(self):
        """Test deserializing data with chapters but no questions."""
        data = {
            "chapters": {"1": "Chapter 1", "2": "Chapter 2"},
            "chap_to_qids": {"1": [], "2": []},
            "questions": {},
            "img_dir": TEST_IMG_DIR
        }

        qb = self.db._deserialize_question_bank(data)

        assert qb.get_all_chapter_num() == [1, 2]
        assert qb.describe_chapter(1) == "Chapter 1"
        assert qb.describe_chapter(2) == "Chapter 2"
        assert qb.question_count() == 0

    def test_deserialize_with_questions(self):
        """Test deserializing data with questions."""
        data = {
            "chapters": {"1": "Chapter 1"},
            "chap_to_qids": {"1": ["q1"]},
            "questions": {
                "q1": {
                    "qid": "q1",
                    "question": "Test question?",
                    "answers": ["Yes", "No", "Maybe"],
                    "correct_answer": "Yes",
                    "img_path": TEST_IMG_DIR + "q1"
                }
            },
            "img_dir": TEST_IMG_DIR
        }

        qb = self.db._deserialize_question_bank(data)

        assert qb.get_all_chapter_num() == [1]
        assert qb.question_count() == 1
        assert qb.get_qids_by_chapter(1) == {"q1"}

        question = qb.get_question("q1")
        assert question.get_question() == "Test question?"
        assert question.get_answers() == {"Yes", "No", "Maybe"}
        assert question.get_correct_answer() == "Yes"
        assert question.get_img_path() == TEST_IMG_DIR + "q1"

    def test_deserialize_maintains_question_properties(self):
        """Test that deserialization maintains all question properties."""
        data = {
            "chapters": {"1": "Chapter 1"},
            "chap_to_qids": {"1": ["q1"]},
            "questions": {
                "q1": {
                    "qid": "q1",
                    "question": "Test question?",
                    "answers": ["A", "B", "C", "D"],
                    "correct_answer": "B",
                    "img_path": TEST_IMG_DIR + "q1"
                }
            },
            "img_dir": TEST_IMG_DIR
        }

        qb = self.db._deserialize_question_bank(data)
        question = qb.get_question("q1")

        # Check all properties were preserved
        assert question.get_qid() == "q1"
        assert question.get_question() == "Test question?"
        assert question.get_answers() == {"A", "B", "C", "D"}
        assert question.get_correct_answer() == "B"
        assert question.get_img_path() == TEST_IMG_DIR + "q1"


class TestCopyImages:
    """Tests for the _copy_images method."""
    def setup_method(self):
        self.db = LocalJsonDB(TEST_DB_PATH, TEST_IMG_DIR)

    def teardown_method(self):
        teardown()

    def test_copy_images_with_no_images(self):
        """Test copying when there are no images in the question bank."""
        qb = QuestionBank(SOURCE_IMG_TEST)
        qb.add_chapter(1, "Chapter 1")

        # Add a question with no image
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"Yes", "No"},
            correct_answer="Yes"
        )
        qb.add_question(question, 1)

        # Should not raise any errors
        self.db._copy_images(qb)

        # No files should be created
        assert len(os.listdir(TEST_IMG_DIR)) == 0

    def test_copy_images_with_existing_images(self):
        """Test copying when images exist in the question bank."""
        # Create a test image in the source directory
        source_img_path = os.path.join(SOURCE_IMG_TEST, "test_img.jpg")
        with open(source_img_path, 'w') as f:
            f.write("dummy image content")

        qb = QuestionBank(SOURCE_IMG_TEST)
        qb.add_chapter(1, "Chapter 1")

        # Add a question with an image
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"Yes", "No"},
            correct_answer="Yes",
            img_path=source_img_path
        )
        qb.add_question(question, 1)

        # This should copy the image
        with patch('src.data_storage.database.local_json_db.shutil.copy2') as mock_copy:
            self.db._copy_images(qb)
            mock_copy.assert_called_once_with(source_img_path, TEST_IMG_DIR + "q1")


class TestIntegration:
    """Integration tests for LocalJsonDB."""

    def setup_method(self):
        """Set up test environment before each test method."""
        self.db = LocalJsonDB(TEST_DB_PATH, TEST_IMG_DIR)

    def teardown_method(self):
        teardown()

    def test_save_and_load_cycle(self):
        """Test saving a question bank and then loading it back."""
        # Create a question bank with test data
        qb_original = QuestionBank(TEST_IMG_DIR)
        qb_original.add_chapter(1, "Chapter 1")
        qb_original.add_chapter(2, "Chapter 2")

        q1 = Question("q1", "Question 1?", {"A", "B", "C"}, "B")
        q2 = Question("q2", "Question 2?", {"X", "Y", "Z"}, "Z")

        qb_original.add_question(q1, 1)
        qb_original.add_question(q2, 2)

        # Save the question bank
        result = self.db.save(qb_original)
        assert result is True

        # Load the question bank back
        qb_loaded = self.db.load()

        # Verify the loaded question bank matches the original
        assert qb_loaded.get_all_chapter_num() == [1, 2]
        assert qb_loaded.describe_chapter(1) == "Chapter 1"
        assert qb_loaded.describe_chapter(2) == "Chapter 2"

        assert qb_loaded.get_qids_by_chapter(1) == {"q1"}
        assert qb_loaded.get_qids_by_chapter(2) == {"q2"}

        q1_loaded = qb_loaded.get_question("q1")
        assert q1_loaded.get_question() == "Question 1?"
        assert q1_loaded.get_answers() == {"A", "B", "C"}
        assert q1_loaded.get_correct_answer() == "B"

        q2_loaded = qb_loaded.get_question("q2")
        assert q2_loaded.get_question() == "Question 2?"
        assert q2_loaded.get_answers() == {"X", "Y", "Z"}
        assert q2_loaded.get_correct_answer() == "Z"

    def test_image_handling_end_to_end(self):
        """Test end-to-end image handling during save and load."""
        # Create a test image
        source_img_path = os.path.join(SOURCE_IMG_TEST, "test_img.jpg")
        with open(source_img_path, 'w') as f:
            f.write("dummy image content")

        # Create a question bank with an image
        qb_original = QuestionBank(SOURCE_IMG_TEST)
        qb_original.add_chapter(1, "Chapter 1")

        q1 = Question(
            qid="q1",
            question="Question with image?",
            answers={"Yes", "No"},
            correct_answer="Yes",
            img_path=source_img_path
        )
        qb_original.add_question(q1, 1)

        # Mock the image copying to verify it's called correctly
        with patch('src.data_storage.database.local_json_db.shutil.copy2') as mock_copy:
            self.db.save(qb_original)
            mock_copy.assert_called_once_with(source_img_path, TEST_IMG_DIR + "q1")

        # Load the question bank back (mocking file operations)
        with patch('builtins.open', mock_open(read_data=json.dumps({
            "chapters": {"1": "Chapter 1"},
            "chap_to_qids": {"1": ["q1"]},
            "questions": {
                "q1": {
                    "qid": "q1",
                    "question": "Question with image?",
                    "answers": ["Yes", "No"],
                    "correct_answer": "Yes",
                    "img_path": TEST_IMG_DIR + "q1"
                }
            },
            "img_dir": TEST_IMG_DIR
        }))):
            qb_loaded = self.db.load()

        # Verify the image path in the loaded question
        q1_loaded = qb_loaded.get_question("q1")
        assert q1_loaded.get_img_path() == TEST_IMG_DIR + "q1"

    def test_persistence_across_instances(self):
        """Test data persistence across different LocalJsonDB instances."""
        # Create and save with first instance
        db1 = LocalJsonDB(TEST_DB_PATH, TEST_IMG_DIR)

        qb = QuestionBank(TEST_IMG_DIR)
        qb.add_chapter(1, "Chapter 1")
        q1 = Question("q1", "Test question?", {"A", "B"}, "A")
        qb.add_question(q1, 1)

        db1.save(qb)

        # Create second instance and load
        db2 = LocalJsonDB(TEST_DB_PATH, TEST_IMG_DIR)
        qb_loaded = db2.load()

        # Verify data was persisted correctly
        assert qb_loaded.get_all_chapter_num() == [1]
        assert qb_loaded.describe_chapter(1) == "Chapter 1"
        assert qb_loaded.get_qids_by_chapter(1) == {"q1"}

        question = qb_loaded.get_question("q1")
        assert question.get_question() == "Test question?"
        assert question.get_answers() == {"A", "B"}
        assert question.get_correct_answer() == "A"
