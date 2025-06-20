# Program for scraping the chinese driving exam question bank off the web
import logging
from logging import Logger
import os
from datetime import datetime

from data_storage.database.database_interface import Database
from data_storage.database.local_json_db import LocalJsonDB
from data_storage.in_memory.question_bank import QuestionBank
from ui.question_displayer import QuestionDisplayer
from ui.console_qdis import ConsoleQuesShower
from scraper.scraper_interface import Scraper
from scraper.jsyks_scraper.jsyks_scraper import JSYKSScraper

LOG_PATH = "logs"
DB_PATH = "data_storage/database/local_json_db/data.json"
DB_IMG_DIR = "data_storage/database/local_json_db/images"
IN_MEM_IMG_DIR = "data_storage/in_memory/img"

def make_logger() -> Logger:
    # Create a logger
    logger = logging.getLogger("drivetest_scraper")
    logger.setLevel(logging.INFO)

    # Create a unique log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_PATH, f"scraper_{timestamp}.log")

    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def scrape(db: Database, logger: Logger):
    logger.info("Creating empty question bank...")
    qb = QuestionBank(IN_MEM_IMG_DIR)
    logger.info("Initializing the scraper...")
    scraper: Scraper = JSYKSScraper(qb, logger)
    logger.info("Starting the scraping process...")
    scraper.fill_question_bank()
    logger.info("Scraping completed. Saving to the database...")
    db.save(qb)
    logger.info("Questions successfully downloaded to database.")

def main():
    logger = make_logger()
    choice = ""
    while choice != "e":
        choice = input("This is a simple scraper for scraping chinese drive "
                       "test questions. \n"
                       "Type (s) to scrape. \n"
                       "Type (v) to view existing question bank.\n"
                       "Type (e) to exit. \n"
                       "Input: ").strip().lower()

        logger.info("Setting up the database...")
        db: Database = LocalJsonDB(DB_PATH, DB_IMG_DIR)

        if choice == "s":
            scrape(db, logger)
            print("Scraping complete.")
        elif choice == "v":
            qb = db.load()
            q_presenter: QuestionDisplayer = ConsoleQuesShower()
            print("Which Chapter would you like to view? \n")
            for chapter_num in qb.get_all_chapter_num():
                print(f"Chapter {chapter_num}: "
                      f"{qb.describe_chapter(chapter_num)}")
            chapter = input("Type the chapter number here: ")
            if chapter.isdigit() and int(chapter) in qb.get_all_chapter_num():
                question_ids = qb.get_qids_by_chapter(int(chapter))
                if not question_ids:
                    print("No questions found for this chapter.")
                else:
                    for qid in question_ids:
                        print(f"Displaying question with ID: {qid}")
                        question = qb.get_question(qid)
                        q_presenter.display_question(question)
                        view_ans = input("Type (a) to view the answer. \n"
                                         "Type any other key to skip. \n"
                                         "Input: ").strip().lower()
                        if view_ans == "a":
                            q_presenter.display_answer(question)
                            _ = input("Type any key to view next question.\n"
                                      "Input: ")
        elif choice == "e":
            print("Closing application.")
        else:
            print("Unrecognized input. Please try again.")


if __name__ == "__main__":
    main()
