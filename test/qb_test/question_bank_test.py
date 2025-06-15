import pytest

from src.data_storage.in_memory.question_bank import QuestionBank
from src.data_storage.in_memory.question import Question

def test_add_chapter_success():
    qb = QuestionBank(img_dir="img/")
    qb.add_chapter(1, "Chapter 1")
    assert 1 in qb._chapters
    assert qb._chapters[1] == "Chapter 1"

def test_add_chapter_duplicate_raises():
    qb = QuestionBank(img_dir="img/")
    qb.add_chapter(1, "Chapter 1")
    with pytest.raises(ValueError):
        qb.add_chapter(1, "Duplicate Chapter")

def test_add_question_success():
    qb = QuestionBank(img_dir="img/")
    qb.add_chapter(1, "Chapter 1")
    q = Question("Q1", "What is 2+2?", {"4", "3"}, "4")
    qb.add_question(q, 1)
    assert "Q1" in qb._ids
    assert "Q1" in qb._chap_num_to_ids[1]
    assert qb._id_to_q["Q1"] == q

def test_add_question_to_nonexistent_chapter_raises():
    qb = QuestionBank(img_dir="img/")
    q = Question("Q1", "What is 2+2?", {"4", "3"}, "4")
    with pytest.raises(KeyError):
        qb.add_question(q, 99)

def test_get_question_success():
    qb = QuestionBank(img_dir="img/")
    qb.add_chapter(1, "Chapter 1")
    q = Question("Q1", "What is 2+2?", {"4", "3"}, "4")
    qb.add_question(q, 1)
    assert qb.get_question("Q1") == q

def test_get_question_not_found_raises():
    qb = QuestionBank(img_dir="img/")
    with pytest.raises(LookupError):
        qb.get_question("QX")

def test_get_qids_by_chapter_success():
    qb = QuestionBank(img_dir="img/")
    qb.add_chapter(1, "Chapter 1")
    q1 = Question("Q1", "What is 2+2?", {"4", "3"}, "4")
    q2 = Question("Q2", "What is 3+3?", {"6", "5"}, "6")
    qb.add_question(q1, 1)
    qb.add_question(q2, 1)
    assert qb.get_qids_by_chapter(1) == {"Q1", "Q2"}

def test_get_qids_by_chapter_not_found_raises():
    qb = QuestionBank(img_dir="img/")
    with pytest.raises(LookupError):
        qb.get_qids_by_chapter(99)

def test_describe_chapter_success():
    qb = QuestionBank(img_dir="img/")
    qb.add_chapter(1, "Chapter 1 Description")
    assert qb.describe_chapter(1) == "Chapter 1 Description"

def test_describe_chapter_not_found_raises():
    qb = QuestionBank(img_dir="img/")
    with pytest.raises(LookupError):
        qb.describe_chapter(99)

def test_get_img_dir_returns_correct_path():
    qb = QuestionBank(img_dir="/tmp/images")
    assert qb.get_img_dir() == "/tmp/images"

def test_get_all_chapter_num_ordered():
    qb = QuestionBank(img_dir="img/")
    qb.add_chapter(2, "Chapter 2")
    qb.add_chapter(1, "Chapter 1")
    qb.add_chapter(3, "Chapter 3")
    assert qb.get_all_chapter_num() == [1, 2, 3]

def test_question_count_total():
    qb = QuestionBank(img_dir="img/")
    qb.add_chapter(1, "Chapter 1")
    qb.add_chapter(2, "Chapter 2")
    qb.add_question(Question("Q1", "A?", {"A", "B"}, "A"), 1)
    qb.add_question(Question("Q2", "B?", {"B", "C"}, "B"), 2)
    qb.add_question(Question("Q3", "C?", {"C", "D"}, "C"), 2)
    assert qb.question_count() == 3

def test_question_count_by_chapter():
    qb = QuestionBank(img_dir="img/")
    qb.add_chapter(1, "Chapter 1")
    qb.add_question(Question("Q1", "A?", {"A", "B"}, "A"), 1)
    qb.add_question(Question("Q2", "B?", {"B", "C"}, "B"), 1)
    assert qb.question_count(1) == 2

def test_question_count_by_nonexistent_chapter_raises():
    qb = QuestionBank(img_dir="img/")
    with pytest.raises(KeyError):
        qb.question_count(99)
