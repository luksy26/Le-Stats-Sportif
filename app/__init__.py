from flask import Flask
from app.data_ingestor import DataIngestor
from app.task_runner import ThreadPool
# from task_runner import ThreadPool
# from data_ingestor import DataIngestor
import pprint

webserver = Flask(__name__)
webserver.tasks_runner = ThreadPool()

# webserver.task_runner.start()

# webserver.data_ingestor = DataIngestor("../nutrition_activity_obesity_usa_subset.csv")
webserver.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")

# with open('formatted_dict.txt', 'w') as file:
#     pprint.pprint(webserver.data_ingestor.questions_dict, stream=file, compact=True)

webserver.job_counter = 1

from app import routes
# import routes


