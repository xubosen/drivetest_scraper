# Library Imports
import pytest
from bs4 import BeautifulSoup

# Module Imports
from scraper.question import Question
from scraper.jsyks_scraper._question_scraper import QuestionScraper

SAMPLE_URL = "https://tiba.jsyks.com/Post/33b74.htm"

SAMPLE_HTML = """
        <div id="question" class="fcc"><h1>
            <strong>
                <a href="/Post/33b74.htm">这个标志是何含义？</a>
            </strong>
            <span>
                <img onclick="vExamTp(this);" src="https://tp.mnks.cn/ExamPic/kmy_136.jpg">
            </span>
            A、注意行人
            <br>B、人行横道
            <br><b>C、注意儿童</b>
            <br>D、学校区域
            <br>答案：<u>C</u></h1>
            <p><i title="人气指数" id="ReadCount">1238753</i></p>
            <b class="bg"></b>
        </div>
        """

QUESTION_IDS = ["c6219", "d150f", "ad9e0", "b5211", "cd86b"]
IMG_PATH = "db_test/img"
CONFIG_PATH = "scraper_test/site_info_test.json"

class TestQuestionScraper:
    """
    Test class for the QuestionScraper.
    """
    scraper: QuestionScraper
    url: str
    webpage: BeautifulSoup | None

    # Set up attributes
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """
        Setup method to initialize the QuestionScraper before each test.
        """
        self.scraper = QuestionScraper(IMG_PATH, CONFIG_PATH)
        self.url = SAMPLE_URL
        self.webpage = None

    def test_format_url(self):
        """
        Test the URL formatting function.
        """
        q_id = "33b74"
        expected_url = "https://tiba.jsyks.com/Post/33b74.htm"
        assert self.scraper._format_url(q_id) == expected_url, \
            "URL formatting failed."

    def test_get_webpage(self):
        """
        Test the webpage fetching function.
        """
        soup = self.scraper._get_webpage(self.url)
        assert isinstance(soup, BeautifulSoup), "Webpage fetching failed."
        if isinstance(soup, BeautifulSoup):
            self.webpage = soup

    def test_extract_question(self):
        """
        Test the _extract_question function with sample HTML.
        """
        soup = self.webpage if self.webpage is not None else BeautifulSoup(SAMPLE_HTML, "html.parser")
        question = self.scraper._extract_question("33b74", soup)
        assert question._qid == "33b74"
        assert question._question == "这个标志是何含义？"
        assert "注意儿童" in question._answers
        assert "人行横道" in question._answers
        assert "学校区域" in question._answers
        assert "注意行人" in question._answers
        assert question._correct_answer == "注意儿童"
        assert question._img_path == "https://tp.mnks.cn/ExamPic/kmy_136.jpg"

    def get_h1(self):
        soup = self.webpage if self.webpage is not None else BeautifulSoup(SAMPLE_HTML, "html.parser")
        return soup.find("h1")

    def test__extract_question_text_from_sample(self):
        assert self.scraper._extract_question_text(
            self.get_h1()
        ) == "这个标志是何含义？"

    def test__extract_img_url_from_sample(self):
        scraper = self.scraper
        h1 = self.get_h1()
        assert scraper._extract_img_url(h1) == "https://tp.mnks.cn/ExamPic/kmy_136.jpg"

    def test__extract_answers_from_sample(self):
        scraper = self.scraper
        h1 = self.get_h1()
        options, correct = scraper._extract_answers(h1)
        assert options == {"注意行人", "人行横道", "注意儿童", "学校区域"}
        assert correct == "注意儿童"
