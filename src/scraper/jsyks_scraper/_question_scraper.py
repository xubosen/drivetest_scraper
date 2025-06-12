# Scrape question content, multiple choice options, and answers using requests
# and BeautifulSoup.

# Library Imports

# Module Import
from scraper.question import Question

class QuestionScraper:
    """
    Scraper that retrieves the content of a question.
    """
    _img_save_path: str

    def __init__(self, img_save_path: str):
        """
        Initializes the QuestionScraper with the site information in the json
        file.
        """
        self._img_save_path = img_save_path

    def get_content(self, q_id: str) -> Question:
        """
        Retrieves the content of a question by its ID.
        :param q_id:
        :return: The Question object containing the question content, options,
        image, and answer.
        """
        # TODO: Implement the logic to scrape the webpage
        raise NotImplementedError
