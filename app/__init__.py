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
import shutil
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

from app import routes

# Get the current working directory
cwd = os.getcwd()

# Define the desired path for the "results" directory
results_dir = os.path.join(cwd, "results")

# Check if the directory exists
if os.path.exists(results_dir):
    # Delete the existing directory and its contents (be cautious!)
    shutil.rmtree(results_dir)
    print("Existing directory 'results' deleted.")
    # Recreate the empty directory
    os.makedirs(results_dir)
    print("Directory 'results' created successfully!")
else:
    # Create the directory if it doesn't exist
    os.makedirs(results_dir)
    print("Directory 'results' created successfully!")
