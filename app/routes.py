"""
Webserver for question data analysis.

- Calculates means & differences for states, categories (state, stratification).
- Handles asynchronous tasks via thread pool.
- Provides API endpoints for job submission and retrieval.

See API endpoints for details (index route displays list).

Requires webserver & data ingestion modules to be configured.
"""
import os
import heapq
import pickle

from flask import request, jsonify
from app import webserver


# Example endpoint definition
@webserver.route('/api/post_endpoint', methods=['POST'])
def post_endpoint():
    """
    Handles POST requests, echoes received JSON data in the response.

    Returns:
        JSON: Response message and received data (on successful POST).
        JSON (405): Error message for non-POST requests.
    """
    if request.method == 'POST':
        # Assuming the request contains JSON data
        data = request.json
        print(f"got data in post {data}")

        # Process the received data
        # For demonstration purposes, just echoing back the received data
        response = {"message": "Received data successfully", "data": data}

        # Sending back a JSON response
        return jsonify(response)

    # Method Not Allowed
    return jsonify({"error": "Method not allowed"}), 405


@webserver.route('/api/get_results/<job_id>', methods=['GET'])
def get_response(job_id):
    """
    Checks job status based on ID.

    Args:
        job_id (int): The ID of the job to inquire about.

    Returns:
        JSON: Response containing job status and data (if done) or error message.
    """
    webserver.my_logger.info(f"Requesting data for job_{job_id}")

    # Check if job_id is valid
    if int(job_id) <= webserver.job_counter:
        # Check if job_id is done and return the result
        task_data = task_data_for(int(job_id), webserver.my_logger)
        if task_data is None:
            webserver.my_logger.info(f"Job {job_id} is running, data cannot be provided yet")

            return jsonify({'status': "running"})

        webserver.my_logger.info(f"Job {job_id} has data {task_data}")

        return jsonify({'status': "done", 'data': task_data})

    # If not, return running status
    webserver.my_logger.info(f"Job {job_id} is invalid")

    return jsonify({'status': "error", 'reason': "Invalid job_id"})


def task_data_for(job_id, my_logger):
    """
    Fetches task data (a dictionary) from job_id.pkl,
    or None if not found.
    """
    results_dir = webserver.tasks_runner.results_dir

    # Construct the filename with .pkl extension
    filename = os.path.join(results_dir, f"{job_id}.pkl")

    # Check if the file exists
    if not os.path.exists(filename):
        return None
    with open(filename, 'rb') as job_file:
        # Load the PKL data from the file
        my_logger.info(f"Found the result file for job {job_id}")
        return pickle.load(job_file)


@webserver.route('/api/states_mean', methods=['POST'])
def states_mean_request():
    """
    Handles requests to calculate state means for a given question.

    - Extracts question text from JSON request data.
    - Submits a job to the thread pool to calculate state means for the question.
    - Increments the job counter.
    - Returns the job ID associated with the submitted task.

    Returns:
        JSON: Response containing the submitted job's ID.
    """
    # check if the threadpool is accepting requests
    webserver.my_logger.info("Requesting states_mean")

    if webserver.tasks_runner.is_shutting_down():
        webserver.my_logger.info("Threadpool is shutting down, "
                                 "states_mean request not accepted")

        return jsonify({"job_id": -1, "reason": "shutting down"})
    # Get request data
    data = request.json
    question = data["question"]
    # Register job. Don't wait for task to finish
    questions_dict = webserver.data_ingestor.questions_dict

    webserver.my_logger.info(f"Submitting new job with id {webserver.job_counter} "
                             f"after states_mean request")

    new_task = (webserver.job_counter, calculate_states_mean, question,
                questions_dict, webserver.logger)
    webserver.tasks_runner.submit(new_task)
    # Increment job_id counter
    webserver.job_counter += 1
    # Return associated job_id
    return jsonify({"job_id": new_task[0]})


def calculate_states_mean(question, questions_dict, my_logger):
    """
    Calculates mean data values for each state across all stratifications
    for a given question.

    Args:
        question (str): The text of the question to calculate state means for.
        questions_dict: the dictionary that contains all the necessary data
        my_logger: useful for debug

    Returns:
        dict: A dictionary with state names as keys and their calculated mean values.
            States are sorted by mean value in ascending order.
    """
    my_logger.info(f"Calculating answer for states_mean and question: {question}")

    result = {}
    states_dict = questions_dict[question]
    for state, stratification_categories_dict in states_dict.items():
        sum_values = 0
        no_values = 0
        for _, stratifications_dict in stratification_categories_dict.items():
            for _, data_values_dict in stratifications_dict.items():
                for _, value in data_values_dict.items():
                    sum_values += float(value)
                    no_values += 1
        if no_values > 0:
            result[state] = sum_values / no_values
    result = dict(sorted(result.items(), key=lambda item: item[1]))

    my_logger.info(f"Got answer for states_mean and question: {question}. Result is {result}")

    return result


@webserver.route('/api/state_mean', methods=['POST'])
def state_mean_request():
    """
    Handles requests to calculate the mean for a given question and state.

    - Extracts question text and state name from JSON request data.
    - Submits a job to the thread pool to calculate the mean for that question and state.
    - Increments the job counter.
    - Returns the job ID associated with the submitted task.

    Returns:
        JSON: Response containing the submitted job's ID.
    """
    webserver.my_logger.info("Requesting state_mean")

    # check if the threadpool is accepting requests
    if webserver.tasks_runner.is_shutting_down():
        webserver.my_logger.info("Threadpool is shutting down, "
                                 "state_mean request not accepted")

        return jsonify({"job_id": -1, "reason": "shutting down"})
    # Get request data
    data = request.json
    question = data["question"]
    state = data["state"]
    # Register job. Don't wait for task to finish
    questions_dict = webserver.data_ingestor.questions_dict

    webserver.my_logger.info(f"Submitting new job with id {webserver.job_counter} "
                             f"after state_mean request")

    new_task = (webserver.job_counter, calculate_state_mean,
                question, state, questions_dict, webserver.my_logger)
    webserver.tasks_runner.submit(new_task)
    # Increment job_id counter
    webserver.job_counter += 1
    # Return associated job_id
    return jsonify({"job_id": new_task[0]})


def calculate_state_mean(question, state, questions_dict, my_logger):
    """
    Calculates the mean data value for a specific question and state across all stratifications.

    Args:
        question (str): The text of the question to calculate the mean for.
        state (str): The name of the state to calculate the mean for.
        questions_dict: the dictionary that contains all the necessary data
        my_logger: useful for debug

    Returns:
        dict: A dictionary with the state name as the key and its calculated mean value.
            Returns an empty dictionary if no data is available for the specified
            question and state.
    """
    my_logger.info(f"Calculating answer for state_mean and question: {question}, state: {state}")

    result = {}
    states_dict = questions_dict[question]
    stratification_categories_dict = states_dict[state]
    sum_values = 0
    no_values = 0
    for _, stratifications_dict in stratification_categories_dict.items():
        for _, data_values_dict in stratifications_dict.items():
            for _, value in data_values_dict.items():
                sum_values += float(value)
                no_values += 1
    if no_values > 0:
        result[state] = sum_values / no_values

    my_logger.info(f"Got answer for state_mean and question: {question}.")

    return result


@webserver.route('/api/best5', methods=['POST'])
def best5_request():
    """
    Handles requests to calculate the top 5 states (or lowest 5 depending on the question)
    based on the data for a given question.

    - Extracts question text from JSON request data.
    - Submits a job to the thread pool to identify the top/bottom 5 states for the question.
    - Increments the job counter.
    - Returns the job ID associated with the submitted task.

    Returns:
        JSON: Response containing the submitted job's ID.
    """
    webserver.my_logger.info("Requesting best5")

    # check if the threadpool is accepting requests
    if webserver.tasks_runner.is_shutting_down():
        webserver.my_logger.info("Threadpool is shutting down, "
                                 "best5 request not accepted")

        return jsonify({"job_id": -1, "reason": "shutting down"})
    # Get request data
    data = request.json
    question = data["question"]
    # Register job. Don't wait for task to finish
    questions_dict = webserver.data_ingestor.questions_dict
    questions_best_is_max = webserver.data_ingestor.questions_best_is_max

    webserver.my_logger.info(f"Submitting new job with id {webserver.job_counter} "
                             f"after best5 request")

    new_task = (webserver.job_counter, calculate_best5, question, questions_dict,
                questions_best_is_max, webserver.my_logger)
    webserver.tasks_runner.submit(new_task)
    # Increment job_id counter
    webserver.job_counter += 1
    # Return associated job_id
    return jsonify({"job_id": new_task[0]})


def calculate_best5(question, questions_dict, questions_best_is_max, my_logger):
    """
    Identifies top/bottom 5 states based on mean values (question-dependent).

    Args:
        question (str): The question to analyze.
        questions_dict: the dictionary that contains all the necessary data
        questions_best_is_max: list of questions for which a larger value is better
        my_logger: useful for debug

    Returns:
        dict: Top/bottom 5 states with mean values (sorted).
    """
    my_logger.info(f"Calculating answer for best5 and question: {question}")

    temp_result = calculate_states_mean(question, questions_dict, my_logger)
    if question in questions_best_is_max:
        result = heapq.nlargest(5, temp_result.items(), key=lambda item: item[1])
        sorted_result = dict(sorted(result, key=lambda item: item[1], reverse=True))
    else:
        result = heapq.nsmallest(5, temp_result.items(), key=lambda item: item[1])
        sorted_result = dict(sorted(result, key=lambda item: item[1]))

    my_logger.info(f"Got answer for best5 and question: {question}. Result is {sorted_result}")

    return sorted_result


@webserver.route('/api/worst5', methods=['POST'])
def worst5_request():
    """
    Similar to 'best5_request' but identifies bottom 5 states based on the question.

    Refer to 'best5_request' docstring for details.

    Returns:
        JSON: Response containing the submitted job's ID.
    """
    webserver.my_logger.info("Requesting worst5")

    # check if the threadpool is accepting requests
    if webserver.tasks_runner.is_shutting_down():
        webserver.my_logger.info("Threadpool is shutting down, "
                                 "worst5 request not accepted")

        return jsonify({"job_id": -1, "reason": "shutting down"})
    # Get request data
    data = request.json
    question = data["question"]
    # Register job. Don't wait for task to finish
    questions_dict = webserver.data_ingestor.questions_dict
    questions_best_is_min = webserver.data_ingestor.questions_best_is_min

    webserver.my_logger.info(f"Submitting new job with id {webserver.job_counter} "
                             f"after worst5 request")

    new_task = (webserver.job_counter, calculate_worst5, question, questions_dict,
                questions_best_is_min, webserver.my_logger)
    webserver.tasks_runner.submit(new_task)
    # Increment job_id counter
    webserver.job_counter += 1
    # Return associated job_id
    return jsonify({"job_id": new_task[0]})


def calculate_worst5(question, questions_dict, questions_best_is_min, my_logger):
    """
    Similar to 'calculate_best5' but identifies bottom 5 states instead of top 5.

    Refer to 'calculate_best5' docstring for details.

    Args:
        question (str): The question to analyze.
        questions_dict: the dictionary that contains all the necessary data
        questions_best_is_min: list of questions for which a smaller value is better
        my_logger: useful for debug

    Returns:
        dict: Bottom 5 states with mean values (sorted).
    """
    my_logger.info(f"Calculating answer for worst5 and question: {question}")

    temp_result = calculate_states_mean(question, questions_dict, my_logger)
    if question in questions_best_is_min:
        result = heapq.nlargest(5, temp_result.items(), key=lambda item: item[1])
        sorted_result = dict(sorted(result, key=lambda item: item[1], reverse=True))
    else:
        result = heapq.nsmallest(5, temp_result.items(), key=lambda item: item[1])
        sorted_result = dict(sorted(result, key=lambda item: item[1]))

    my_logger.info(f"Got answer for worst5 and question: {question}. Result is {sorted_result}")

    return sorted_result


@webserver.route('/api/global_mean', methods=['POST'])
def global_mean_request():
    """
    Handles requests to calculate the global mean for a given question.

    - Extracts question text from JSON request data.
    - Submits a job to the thread pool to calculate the global mean for the question.
    - Increments the job counter.
    - Returns the job ID associated with the submitted task.

    Returns:
        JSON: Response containing the submitted job's ID.
    """
    webserver.my_logger.info("Requesting global_mean")

    # check if the threadpool is accepting requests
    if webserver.tasks_runner.is_shutting_down():
        webserver.my_logger.info("Threadpool is shutting down, "
                                 "global_mean request not accepted")

        return jsonify({"job_id": -1, "reason": "shutting down"})
    # Get request data
    data = request.json
    question = data["question"]
    # Register job. Don't wait for task to finish
    questions_dict = webserver.data_ingestor.questions_dict

    webserver.my_logger.info(f"Submitting new job with id {webserver.job_counter} "
                             f"after global_mean request")

    new_task = (webserver.job_counter, calculate_global_mean,
                question, questions_dict, webserver.my_logger)
    webserver.tasks_runner.submit(new_task)
    # Increment job_id counter
    webserver.job_counter += 1
    # Return associated job_id
    return jsonify({"job_id": new_task[0]})


def calculate_global_mean(question, questions_dict, my_logger):
    """
    Calculates the overall mean value for a given question across all states and stratifications.

    Args:
        question (str): The text of the question to calculate the global mean for.
        questions_dict: the dictionary that contains all the necessary data
        my_logger: useful for debug

    Returns:
        dict: A dictionary containing the global mean value under the key "global_mean".
            Returns an empty dictionary if no data is available for the specified question.
    """
    my_logger.info(f"Calculating answer for global_mean and question: {question}")

    result = {}
    sum_values = 0
    no_values = 0
    states_dict = questions_dict[question]
    for _, stratification_categories_dict in states_dict.items():
        for _, stratifications_dict in stratification_categories_dict.items():
            for _, data_values_dict in stratifications_dict.items():
                for _, value in data_values_dict.items():
                    sum_values += float(value)
                    no_values += 1
    result["global_mean"] = 0
    if no_values > 0:
        result["global_mean"] = sum_values / no_values

    my_logger.info(f"Got answer for global_mean and question: {question}. Result is {result}")

    return result


@webserver.route('/api/diff_from_mean', methods=['POST'])
def diff_from_mean_request():
    """
    Handles requests to calculate the difference from the global mean for a given question.

    - Extracts question text from JSON request data.
    - Submits a job to the thread pool to calculate the difference from the global mean
    for each state.
    - Increments the job counter.
    - Returns the job ID associated with the submitted task.

    Returns:
        JSON: Response containing the submitted job's ID.
    """
    webserver.my_logger.info("Requesting diff_from_mean")

    # check if the threadpool is accepting requests
    if webserver.tasks_runner.is_shutting_down():
        webserver.my_logger.info("Threadpool is shutting down, "
                                 "diff_from_mean request not accepted")

        return jsonify({"job_id": -1, "reason": "shutting down"})
    # Get request data
    data = request.json
    question = data["question"]
    # Register job. Don't wait for task to finish
    questions_dict = webserver.data_ingestor.questions_dict

    webserver.my_logger.info(f"Submitting new job with id {webserver.job_counter} "
                             f"after diff_from_mean request")

    new_task = (webserver.job_counter, calculate_diff_from_mean,
                question, questions_dict, webserver.my_logger)
    webserver.tasks_runner.submit(new_task)
    # Increment job_id counter
    webserver.job_counter += 1
    # Return associated job_id
    return jsonify({"job_id": new_task[0]})


def calculate_diff_from_mean(question, questions_dict, my_logger):
    """
    Calculates state differences from global mean for a question.

    Args:
        question (str): The question to analyze.
        questions_dict: the dictionary that contains all the necessary data
        my_logger: useful for debug

    Returns:
        dict: State names with differences from global mean.
    """
    my_logger.info(f"Calculating answer for diff_from_mean and question: {question}")

    global_mean = calculate_global_mean(question, questions_dict, my_logger)
    states_mean = calculate_states_mean(question, questions_dict, my_logger)
    result = {key: global_mean["global_mean"] - value for key, value in states_mean.items()}

    my_logger.info(f"Got answer for diff_from_mean and question: {question}. Result is {result}")

    return result


@webserver.route('/api/state_diff_from_mean', methods=['POST'])
def state_diff_from_mean_request():
    """
    Similar to 'diff_from_mean_request' but calculates difference for a specific state.

    - Extracts question text and state name from JSON request data.
    - Submits a job to calculate the difference from the global mean for the specified state.
    - Increments the job counter.
    - Returns the job ID associated with the submitted task.

    Returns:
        JSON: Response containing the submitted job's ID.
    """
    webserver.my_logger.info("Requesting state_diff_from_mean")

    # check if the threadpool is accepting requests
    if webserver.tasks_runner.is_shutting_down():
        webserver.my_logger.info("Threadpool is shutting down, "
                                 "state_diff_from_mean request not accepted")

        return jsonify({"job_id": -1, "reason": "shutting down"})
    # Get request data
    data = request.json
    question = data["question"]
    state = data["state"]
    # Register job. Don't wait for task to finish
    questions_dict = webserver.data_ingestor.questions_dict

    webserver.my_logger.info(f"Submitting new job with id {webserver.job_counter} "
                             f"after state_diff_from_mean request")

    new_task = (webserver.job_counter, calculate_state_diff_from_mean,
                question, state, questions_dict, webserver.my_logger)
    webserver.tasks_runner.submit(new_task)
    # Increment job_id counter
    webserver.job_counter += 1
    # Return associated job_id
    return jsonify({"job_id": new_task[0]})


def calculate_state_diff_from_mean(question, state, questions_dict, my_logger):
    """
    Calculates difference between global mean and state mean for a question and state.

    Args:
        question (str): The question to analyze.
        state (str): The state to compare.
        questions_dict: the dictionary that contains all the necessary data
        my_logger: useful for debug

    Returns:
        dict: State and its difference from global mean.
    """
    my_logger.info(f"Calculating answer for state_diff_from_mean "
                   f"and question: {question}, state: {state}")

    global_mean = calculate_global_mean(question, questions_dict, my_logger)
    state_mean = calculate_state_mean(question, state, questions_dict, my_logger)

    result = {state: global_mean["global_mean"] - state_mean[state]}

    my_logger.info(f"Got answer for state_diff_from_mean "
                   f"and question: {question}, state: {state}. Result is {result}")

    return result


@webserver.route('/api/mean_by_category', methods=['POST'])
def mean_by_category_request():
    """
    Handles requests to calculate mean values for each category within a question.

    - Extracts question text from JSON request data.
    - Submits a job to the thread pool to calculate mean values by category for the question.
    - Increments the job counter.
    - Returns the job ID associated with the submitted task.

    Returns:
        JSON: Response containing the submitted job's ID.
    """
    webserver.my_logger.info("Requesting mean_by_category")

    # check if the threadpool is accepting requests
    if webserver.tasks_runner.is_shutting_down():
        webserver.my_logger.info("Threadpool is shutting down, "
                                 "mean_by_category request not accepted")

        return jsonify({"job_id": -1, "reason": "shutting down"})
    # Get request data
    data = request.json
    question = data["question"]
    # Register job. Don't wait for task to finish
    questions_dict = webserver.data_ingestor.questions_dict

    webserver.my_logger.info(f"Submitting new job with id {webserver.job_counter} "
                             f"after mean_by_category request")

    new_task = (webserver.job_counter, calculate_mean_by_category,
                question, questions_dict, webserver.my_logger)
    webserver.tasks_runner.submit(new_task)
    # Increment job_id counter
    webserver.job_counter += 1
    # Return associated job_id
    return jsonify({"job_id": new_task[0]})


def calculate_mean_by_category(question, questions_dict, my_logger):
    """
    Calculates mean values for each category (state, stratification category, stratification)
    within a question.

    - Iterates through question data structure to calculate mean for each combination of
    state, stratification category, and stratification.
    - Skips empty categories or stratifications to avoid division by zero.

    Args:
        question (str): The text of the question to analyze.
        questions_dict: the dictionary that contains all the necessary data
        my_logger: useful for debug


    Returns:
        dict: A dictionary with keys representing category combinations
        (state, stratification category, stratification) and their corresponding mean values.
    """
    my_logger.info(f"Calculating answer for mean_by_category and question: {question}")

    result = {}
    states_dict = questions_dict[question]
    for state, stratification_categories_dict in states_dict.items():
        for stratification_category, stratifications_dict in stratification_categories_dict.items():
            for stratification, data_values_dict in stratifications_dict.items():
                sum_values = 0
                no_values = 0
                for _, value in data_values_dict.items():
                    sum_values += float(value)
                    no_values += 1
                if no_values > 0 and stratification_category != "" and stratification != "":
                    new_key = ("(\'" + state + "\', \'" + stratification_category +
                               "\', \'" + stratification + "\')")
                    result[new_key] = sum_values / no_values

    my_logger.info(f"Got answer for mean_by_category and question: {question}. Result is {result}")

    return result


@webserver.route('/api/state_mean_by_category', methods=['POST'])
def state_mean_by_category_request():
    """
    Similar to 'mean_by_category_request' but calculates means within a specific state.

    - Extracts question text and state name from JSON request data.
    - Submits a job to calculate mean values by category for the specified state
    within the question.
    - Increments the job counter.
    - Returns the job ID associated with the submitted task.

    Returns:
        JSON: Response containing the submitted job's ID.
    """
    webserver.my_logger.info("Requesting state_mean_by_category")

    # check if the threadpool is accepting requests
    if webserver.tasks_runner.is_shutting_down():
        webserver.my_logger.info("Threadpool is shutting down, "
                                 "state_mean_by_category request not accepted")

        return jsonify({"job_id": -1, "reason": "shutting down"})
    # Get request data
    data = request.json
    question = data["question"]
    state = data["state"]
    # Register job. Don't wait for task to finish
    questions_dict = webserver.data_ingestor.questions_dict

    webserver.my_logger.info(f"Submitting new job with id {webserver.job_counter} "
                             f"after state_mean_by_category request")

    new_task = (webserver.job_counter, calculate_state_mean_by_category,
                question, state, questions_dict, webserver.my_logger)
    webserver.tasks_runner.submit(new_task)
    # Increment job_id counter
    webserver.job_counter += 1
    # Return associated job_id
    return jsonify({"job_id": new_task[0]})


def calculate_state_mean_by_category(question, state, questions_dict, my_logger):
    """
    Calculates mean values for categories within a specific state of a question.

    - Iterates through the specified state's data to calculate means for each combination of
    stratification category and stratification.
    - Skips empty categories or stratifications to avoid division by zero.

    Args:
        question (str): The text of the question to analyze.
        state (str): The name of the state to calculate means for.
        questions_dict: the dictionary that contains all the necessary data
        my_logger: useful for debug


    Returns:
        dict: A dictionary with the state name as the key and a nested dictionary containing
        mean values for category combinations (stratification category, stratification).
    """
    my_logger.info(f"Calculating answer for state_mean_by_category "
                   f"and question: {question}, state: {state}")

    result = {state: {}}
    states_dict = questions_dict[question]
    stratification_categories_dict = states_dict[state]
    for stratification_category, stratifications_dict in stratification_categories_dict.items():
        for stratification, data_values_dict in stratifications_dict.items():
            sum_values = 0
            no_values = 0
            for _, value in data_values_dict.items():
                sum_values += float(value)
                no_values += 1
            if no_values > 0 and stratification_category != "" and stratification != "":
                new_key = "(\'" + stratification_category + "\', \'" + stratification + "\')"
                result[state][new_key] = sum_values / no_values

    my_logger.info(f"Got answer for state_mean_by_category "
                   f"and question: {question}, state: {state}.")

    return result


@webserver.route('/api/graceful_shutdown', methods=['GET'])
def graceful_shutdown_request():
    """
    Gracefully shuts down the ThreadPool task runner.

    Returns:
        JSONResponse: 202 Accepted response with shutdown message.
    """
    webserver.my_logger.info("Requesting threadpool shutdown")
    webserver.tasks_runner.shutdown()
    return jsonify({'message': 'Graceful shutdown initiated'}), 202


@webserver.route('/api/num_jobs', methods=['GET'])
def num_jobs_request():
    """
    Gets the number of tasks yet to be processed.
    """
    webserver.my_logger.info("Requesting number of running jobs")
    results_dir = webserver.tasks_runner.results_dir
    num_processed = len(os.listdir(results_dir))
    num_encountered = len(webserver.tasks_runner.encountered_tasks)
    num_jobs = num_encountered - num_processed
    webserver.my_logger.info(f"There are {num_jobs} jobs running")
    return jsonify({'Number of tasks': num_jobs}), 200


@webserver.route('/api/jobs', methods=['GET'])
def jobs_request():
    """
    Gets completed & running jobs info, sorts by ID.

    Returns:
        JSONResponse: Status ("done"), data (job_id: "done" or "running"), sorted by ID.
    """
    webserver.my_logger.info("Requesting data about jobs")
    return_data = {"status": "done", "data": []}
    results_dir = webserver.tasks_runner.results_dir
    # Iterate through files in the results directory
    webserver.my_logger.info("Searching for finished jobs")
    for filename in os.listdir(results_dir):
        # Extract job ID from filename
        job_id = int(filename.split(".")[0])
        return_data["data"].append({"job_id_" + str(job_id): "done"})

    potential_running_jobs = webserver.tasks_runner.encountered_tasks
    webserver.my_logger.info("Searching for running jobs")
    for job_id in potential_running_jobs:
        key_to_search = "job_id_" + str(job_id)
        if {key_to_search: "done"} not in return_data["data"]:
            return_data["data"].append({key_to_search: "running"})

    # sorts the list of dictionaries by the job_id (obtained by split)
    # in the key of the first item in each dictionary
    return_data["data"] = sorted(return_data["data"],
                                 key=lambda item: int(list(item.keys())[0].split("_")[2]))

    return jsonify(return_data), 200


# You can check localhost in your browser to see what this displays
@webserver.route('/')
@webserver.route('/index')
def index():
    """
    Generates a basic landing page for the webserver.

    - Retrieves a list of defined routes.
    - Constructs an HTML page with a welcome message and lists all available routes.

    Returns:
      str: An HTML page content string.
    """
    routes = get_defined_routes()
    msg = "Hello, World!\n Interact with the webserver using one of the defined routes:\n"

    # Display each route as a separate HTML <p> tag
    paragraphs = ""
    for route in routes:
        paragraphs = "".join([f"<p>{route}</p>" for route in routes])

    msg += paragraphs
    return msg


def get_defined_routes():
    """
    Extracts a list of all defined routes for the webserver.

    - Iterates through the webserver's URL map to find defined routes.
    - Constructs a list containing route details (endpoint URL and allowed methods) for each route.

    Returns:
      list: A list of strings, where each string represents a route with its endpoint URL
      and allowed methods.
    """
    routes = []
    for rule in webserver.url_map.iter_rules():
        methods = ', '.join(rule.methods)
        routes.append(f"Endpoint: \"{rule}\" Methods: \"{methods}\"")
    return routes
