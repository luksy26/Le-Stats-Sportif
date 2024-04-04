"""
Flask app for data analysis tasks.

* Manages a thread pool.
* Reads data from "nutrition_activity_obesity_usa_subset.csv".
* Stores processed data in `DataIngestor.questions_dict`.
* Tracks jobs with `webserver.job_counter`.
* Creates the 'results' directory that is used by taskRunners to store
the result data for a certain job_id
"""

import pprint
import os
from flask import Flask
from app.data_ingestor import DataIngestor
from app.task_runner import ThreadPool

webserver = Flask(__name__)
webserver.tasks_runner = ThreadPool()

# webserver.task_runner.start()

# webserver.data_ingestor = DataIngestor("../nutrition_activity_obesity_usa_subset.csv")
webserver.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")

# with open('formatted_dict.txt', 'w') as file:
#     pprint.pprint(webserver.data_ingestor.questions_dict, stream=file, compact=True)

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

from app import routes
