"""
Flask app for data analysis tasks.

* Manages a thread pool.
* Reads data from "nutrition_activity_obesity_usa_subset.csv".
* Stores processed data in `DataIngestor.questions_dict`.
* Tracks jobs with `webserver.job_counter` (commented out).
"""

import pprint
from flask import Flask
from app import routes
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
