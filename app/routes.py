from app import webserver
from flask import request, jsonify
# from __init__ import webserver

import os
import json

threadpool = webserver.tasks_runner
ingested_data = webserver.data_ingestor


# Example endpoint definition
@webserver.route('/api/post_endpoint', methods=['POST'])
def post_endpoint():
    if request.method == 'POST':
        # Assuming the request contains JSON data
        data = request.json
        print(f"got data in post {data}")

        # Process the received data
        # For demonstration purposes, just echoing back the received data
        response = {"message": "Received data successfully", "data": data}

        # Sending back a JSON response
        return jsonify(response)
    else:
        # Method Not Allowed
        return jsonify({"error": "Method not allowed"}), 405


@webserver.route('/api/get_results/<job_id>', methods=['GET'])
def get_response(job_id):
    print(f"JobID is {job_id}")
    # Check if job_id is valid
    if int(job_id) <= webserver.job_counter:
        # Check if job_id is done and return the result
        task_data = task_data_for(int(job_id))
        if task_data is None:
            return jsonify({'status': "running"})
        else:
            return jsonify({'status': "done", 'data': task_data})

    # If not, return running status
    else:
        return jsonify({'status': "error", 'reason': "Invalid job_id"})


def task_data_for(job_id):
    for task in threadpool.result_list:
        if task[0] == job_id:
            return task[1]
    return None


@webserver.route('/api/states_mean', methods=['POST'])
def states_mean_request():
    # Get request data
    data = request.json
    question = data["question"]

    # Register job. Don't wait for task to finish
    new_task = (webserver.job_counter, calculate_states_mean, question)
    threadpool.submit(new_task)
    # Increment job_id counter
    webserver.job_counter += 1
    # Return associated job_id
    return jsonify({"job_id": new_task[0]})


def calculate_states_mean(question):
    result = {}
    states_dict = ingested_data.questions_dict[question]
    for state, stratification_categories_dict in states_dict.items():
        sum_values = 0
        no_values = 0
        for stratification_category, stratifications_dict in stratification_categories_dict.items():
            for stratification, data_values_dict in stratifications_dict.items():
                for year, value in data_values_dict.items():
                    sum_values += float(value)
                    no_values += 1
        if no_values > 0:
            result[state] = sum_values / no_values
    return dict(sorted(result.items(), key=lambda item: item[1]))


# print(calculate_states_mean("Percent of adults aged 18 years and older who have an overweight classification"))


@webserver.route('/api/state_mean', methods=['POST'])
def state_mean_request():
    # TODO
    # Get request data
    # Register job. Don't wait for task to finish
    # Increment job_id counter
    # Return associated job_id
    job_id = webserver.job_counter
    webserver.job_counter += 1
    return jsonify({"job_id": job_id})


@webserver.route('/api/best5', methods=['POST'])
def best5_request():
    # TODO
    # Get request data
    # Register job. Don't wait for task to finish
    # Increment job_id counter
    # Return associated job_id

    job_id = webserver.job_counter
    webserver.job_counter += 1
    return jsonify({"job_id": job_id})


@webserver.route('/api/worst5', methods=['POST'])
def worst5_request():
    # TODO
    # Get request data
    # Register job. Don't wait for task to finish
    # Increment job_id counter
    # Return associated job_id

    job_id = webserver.job_counter
    webserver.job_counter += 1
    return jsonify({"job_id": job_id})


@webserver.route('/api/global_mean', methods=['POST'])
def global_mean_request():
    # TODO
    # Get request data
    # Register job. Don't wait for task to finish
    # Increment job_id counter
    # Return associated job_id

    job_id = webserver.job_counter
    webserver.job_counter += 1
    return jsonify({"job_id": job_id})


@webserver.route('/api/diff_from_mean', methods=['POST'])
def diff_from_mean_request():
    # TODO
    # Get request data
    # Register job. Don't wait for task to finish
    # Increment job_id counter
    # Return associated job_id

    job_id = webserver.job_counter
    webserver.job_counter += 1
    return jsonify({"job_id": job_id})


@webserver.route('/api/state_diff_from_mean', methods=['POST'])
def state_diff_from_mean_request():
    # TODO
    # Get request data
    # Register job. Don't wait for task to finish
    # Increment job_id counter
    # Return associated job_id

    job_id = webserver.job_counter
    webserver.job_counter += 1
    return jsonify({"job_id": job_id})


@webserver.route('/api/mean_by_category', methods=['POST'])
def mean_by_category_request():
    # TODO
    # Get request data
    # Register job. Don't wait for task to finish
    # Increment job_id counter
    # Return associated job_id

    job_id = webserver.job_counter
    webserver.job_counter += 1
    return jsonify({"job_id": job_id})


@webserver.route('/api/state_mean_by_category', methods=['POST'])
def state_mean_by_category_request():
    # TODO
    # Get request data
    # Register job. Don't wait for task to finish
    # Increment job_id counter
    # Return associated job_id

    job_id = webserver.job_counter
    webserver.job_counter += 1
    return jsonify({"job_id": job_id})


# You can check localhost in your browser to see what this displays
@webserver.route('/')
@webserver.route('/index')
def index():
    routes = get_defined_routes()
    msg = f"Hello, World!\n Interact with the webserver using one of the defined routes:\n"

    # Display each route as a separate HTML <p> tag
    paragraphs = ""
    for route in routes:
        paragraphs += f"<p>{route}</p>"

    msg += paragraphs
    return msg


def get_defined_routes():
    routes = []
    for rule in webserver.url_map.iter_rules():
        methods = ', '.join(rule.methods)
        routes.append(f"Endpoint: \"{rule}\" Methods: \"{methods}\"")
    return routes
