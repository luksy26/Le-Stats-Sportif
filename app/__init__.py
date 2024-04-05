"""
Flask app for data analysis tasks.

* Manages a thread pool.
* Reads data from "nutrition_activity_obesity_usa_subset.csv".
* Stores processed data in `DataIngestor.questions_dict`.
* Tracks jobs with `webserver.job_counter`.
* Creates the 'results' directory that is used by taskRunners to store
the result data for a certain job_id
"""

import os
import logging
from datetime import timezone
from logging.handlers import RotatingFileHandler
from flask import Flask
from app.data_ingestor import DataIngestor
from app.task_runner import ThreadPool

webserver = Flask(__name__)
webserver.tasks_runner = ThreadPool()

# webserver.task_runner.start()

webserver.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")

webserver.job_counter = 1

# Get the current working directory
cwd = os.getcwd()

# Define the desired path for the "results" directory
results_dir = os.path.join(cwd, "results")

# Ensure the directory exists (create if needed)
os.makedirs(results_dir, exist_ok=True)

# Use os.system to clear contents of the directory
os.system("rm -rf results/*")
print("Empty 'results' directory created successfully")

webserver.tasks_runner.update_results_dir(results_dir)


class UTCFormatter(logging.Formatter):
    """
    Formatter class that ensures UTC timestamps in log messages.
    """
    def formatTime(self, record, datefmt=None):
        timestamp = self.converter(record.created)
        utc_timestamp = timestamp.astimezone(timezone.utc)
        record.created = utc_timestamp
        return super().formatTime(record, datefmt)


def get_logger():
    """
    Creates and returns a logger with UTC timestamps and a rotating file handler.
    """

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    handler = RotatingFileHandler("webserver.log", maxBytes=10485760, backupCount=5)
    formatter = UTCFormatter("%(asctime)s - %(levelname)s - %(message)s",
                             datefmt="%Y-%m-%d %H:%M:%S %Z")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


webserver.my_logger = get_logger()

from app import routes
