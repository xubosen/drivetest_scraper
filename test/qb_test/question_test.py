import pytest

from src.data_storage.in_memory.question import Question, IncorrectFormatError

def test_valid_question_creation():
    q = Question(
        qid="q1",
        question="What is the capital of France?",
        answers={"Paris", "London", "Berlin"},
        correct_answer="Paris",
        img_path="img/france.png"
    )
    assert q.get_qid() == "q1"
    assert q.get_question() == "What is the capital of France?"
    assert q.get_answers() == {"Paris", "London", "Berlin"}
    assert q.get_correct_answer() == "Paris"
    assert q.get_img_path() == "img/france.png"

def test_valid_question_no_img():
    q = Question(
        qid="q2",
        question="What is 2+2?",
        answers={"3", "4"},
        correct_answer="4"
    )
    assert q.get_img_path() is None

def test_invalid_qid():
    with pytest.raises(IncorrectFormatError):
        Question(
            qid="",
            question="Test?",
            answers={"A", "B"},
            correct_answer="A"
        )
    with pytest.raises(IncorrectFormatError):
        Question(
            qid=None,  # type: ignore
            question="Test?",
            answers={"A", "B"},
            correct_answer="A"
        )

def test_invalid_question_text():
    with pytest.raises(IncorrectFormatError):
        Question(
            qid="q3",
            question="",
            answers={"A", "B"},
            correct_answer="A"
        )
    with pytest.raises(IncorrectFormatError):
        Question(
            qid="q3",
            question=None,  # type: ignore
            answers={"A", "B"},
            correct_answer="A"
        )

def test_invalid_answers_set():
    with pytest.raises(IncorrectFormatError):
        Question(
            qid="q4",
            question="Test?",
            answers={"A"},
            correct_answer="A"
        )
    with pytest.raises(IncorrectFormatError):
        Question(
            qid="q4",
            question="Test?",
            answers=[],  # type: ignore
            correct_answer="A"
        )
    with pytest.raises(IncorrectFormatError):
        Question(
            qid="q4",
            question="Test?",
            answers={"A", ""},
            correct_answer="A"
        )

def test_invalid_correct_answer():
    with pytest.raises(IncorrectFormatError):
        Question(
            qid="q5",
            question="Test?",
            answers={"A", "B"},
            correct_answer="C"
        )
    with pytest.raises(IncorrectFormatError):
        Question(
            qid="q5",
            question="Test?",
            answers={"A", "B"},
            correct_answer=None  # type: ignore
        )

def test_invalid_img_path():
    with pytest.raises(IncorrectFormatError):
        Question(
            qid="q6",
            question="Test?",
            answers={"A", "B"},
            correct_answer="A",
            img_path=123  # type: ignore
        )

def test_getters():
    q = Question(
        qid="qid",
        question="Q?",
        answers={"X", "Y"},
        correct_answer="X",
        img_path=None
    )
    assert q.get_qid() == "qid"
    assert q.get_question() == "Q?"
    assert q.get_answers() == {"X", "Y"}
    assert q.get_correct_answer() == "X"
    assert q.get_img_path() is None
