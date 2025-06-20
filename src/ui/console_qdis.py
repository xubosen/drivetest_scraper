# A simple presenter that prints questions to the console.
from PIL import Image

from data_storage.in_memory.question import Question
from ui.question_displayer import QuestionDisplayer

class ConsoleQuesShower(QuestionDisplayer):
    """
    A simple presenter that prints questions and answers to the python console.
    """

    def __init__(self):
        pass

    def display_question(self, question: Question) -> None:
        print(question.get_question())
        q_img_path = question.get_img_path()
        if q_img_path is not None:
            print(f"Image path: {q_img_path}")
            try:
                img = Image.open(q_img_path)
                img.show()
            except Exception as e:
                print(f"Error displaying image: {e}")
        for ans in question.get_answers():
            print(f"- {ans}")

    def display_answer(self, question: Question) -> None:
        print(f"Answer: {question.get_correct_answer()}")
