# DriveTest Scraper

A Python application for scraping and managing Chinese driving exam questions.

## Overview

DriveTest Scraper allows you to download Chinese driving test questions from 
online sources and store them locally for offline study. The application 
provides a simple console interface to scrape questions and view them organized 
by chapter.

## Project Structure

```
drivetest_scraper/
├── logs/                      # Log files directory
├── src/
│   ├── data_storage/
│   │   ├── database/          # Database implementations
│   │   │   ├── local_json_db/ # JSON database implementation
│   │   │   └── database_interface.py
│   │   └── in_memory/         # In-memory data structures
│   │       ├── img/           # Directory for in-memory images
│   │       ├── question.py    # Question data class
│   │       └── question_bank.py # Question collection manager
│   ├── scraper/
│   │   ├── jsyks_scraper/     # Implementation for jsyks website
│   │   └── scraper_interface.py
│   ├── ui/
│   │   ├── console_qdis.py    # Console question display
│   │   └── question_displayer.py
│   └── main.py                # Main application entry point
└── README.md
```

## Core Components

- **QuestionBank**: Manages a collection of questions organized by chapters
- **Question**: Represents a single question with text, answers, and optional image
- **Database**: Interface for persisting question data
- **Scraper**: Interface for web scraping implementations
- **QuestionDisplayer**: Interface for displaying questions to users

## Logging

The application creates detailed logs in the `logs/` directory. Each log file is named with a timestamp for easy tracking and debugging.

## Data Storage

Questions are stored in:
- **In-memory**: During application runtime using `QuestionBank` class
- **Persistent storage**: Using a JSON file database implementation

## Dependencies

- Python 3.6+
- Required Python packages (specified in requirements.txt)

## License

[Specify your license here, e.g., MIT, GPL, etc.]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

