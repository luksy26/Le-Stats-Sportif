"""
Flask app for data analysis tasks.

* Manages a thread pool.
* Reads data from "nutrition_activity_obesity_usa_subset.csv".
* Stores processed data in `DataIngestor.questions_dict`.
* Tracks jobs with `webserver.job_counter`.
* Creates the 'results' directory that is used by taskRunners to store
the result data for a certain job_id
* Creates and assigns a logger to the webserver
"""
import os
import logging
import queue
from logging.handlers import RotatingFileHandler
import time
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


class GMTFormatter(logging.Formatter):
    """
    Formatter class that uses gmtime
    """
    converter = time.gmtime


def get_webserver_logger():
    """
    Configures a logger to be used for the webserver.
    Uses a RotatingFileHandler and a queue listener for multithreading
    """
    # Create logger
    logger = logging.getLogger('webserver_logger')
    logger.setLevel(logging.INFO)

    # Create a Queue to store log records
    log_queue = queue.Queue()

    # Create a rotating file handler
    handler = RotatingFileHandler('webserver.log', maxBytes=1024 * 1024, backupCount=5)

    # Set formatter with GMT timestamp
    formatter = GMTFormatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    # Create and start a QueueListener
    listener = logging.handlers.QueueListener(log_queue, handler)
    listener.start()

    return logger


webserver.my_logger = get_webserver_logger()

from app import routes
