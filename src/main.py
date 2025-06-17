# Program for scraping the chinese driving exam question bank off the web
import logging
from logging import Logger
import os
from datetime import datetime

from data_storage.database.local_json_db import LocalJsonDB
from data_storage.in_memory.question_bank import QuestionBank
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

def main():
    logger = make_logger()
    logger.info("Setting up the database...")
    db = LocalJsonDB(DB_PATH, DB_IMG_DIR)
    logger.info("Creating empty question bank...")
    qb = QuestionBank(IN_MEM_IMG_DIR)
    logger.info("Initializing the scraper...")
    scraper = JSYKSScraper(qb, logger)
    logger.info("Starting the scraping process...")
    scraper.fill_question_bank()
    logger.info("Scraping completed. Saving to the database...")
    db.save(qb)
    logger.info("Scraping completed.")

if __name__ == "__main__":
    main()
