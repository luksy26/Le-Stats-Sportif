"""
Provides a ThreadPool class for managing asynchronous task execution.
"""

import json
import os
import queue
import time
from threading import Thread, Event


class ThreadPool:
    """
    Manages a pool of worker threads

    - Utilizes environment variable 'TP_NUM_OF_THREADS' to configure thread count
    (default: CPU cores).
    - Provides methods to submit tasks, wait for completion, and shut down gracefully.
    """

    def __init__(self):
        # You must implement a ThreadPool of TaskRunners
        # Your ThreadPool should check if an environment variable TP_NUM_OF_THREADS is defined
        # If the env var is defined, that is the number of threads to be used by the thread pool
        # Otherwise, you are to use what the hardware concurrency allows
        # You are free to write your implementation as you see fit, but
        # You must NOT:
        #   * create more threads than the hardware concurrency allows
        #   * recreate threads for each task

        self.num_threads = int(os.getenv("TP_NUM_OF_THREADS", os.cpu_count() or 1))
        self.task_queue = queue.Queue()
        self.results_dir = ""
        self.shutdown_event = Event()
        self.task_runners = []

        # Create and start TaskRunner threads
        for _ in range(self.num_threads):
            task_runner = TaskRunner(self.task_queue, self.results_dir, self.shutdown_event)
            task_runner.start()
            self.task_runners.append(task_runner)

    def submit(self, task):
        """
        Submits a task (function, arguments) to the queue for asynchronous execution.
        """
        self.task_queue.put(task)

    def shutdown(self):
        """
        Initiates a graceful shutdown of the thread pool.

        - Signals worker threads to stop accepting new tasks.
        - Waits for all pending tasks to complete.
        - Joins worker threads to ensure proper termination.
        """
        self.shutdown_event.set()
        # Wait for tasks to finish before joining threads
        self.wait_for_completion()
        for task_runner in self.task_runners:
            task_runner.join()

    def wait_for_completion(self):
        """
        Waits for all tasks currently in the queue to be processed before returning.

        - Polls the task queue to check if it's empty.
        - Introduces a short sleep to avoid busy waiting.
        """
        while not self.task_queue.empty():
            time.sleep(0.1)  # Short wait to avoid busy waiting

    def update_results_dir(self, results_dir):
        self.results_dir = results_dir
        for task_runner in self.task_runners:
            task_runner.results_dir = results_dir


class TaskRunner(Thread):
    """
    Worker thread responsible for retrieving tasks from the queue and executing them.

    - Continuously checks for tasks until signaled to shut down.
    - Executes retrieved tasks and stores results in a shared list.
    """

    def __init__(self, task_queue, results_dir, shutdown_event):
        super().__init__()
        self.task_queue = task_queue
        self.results_dir = results_dir
        self.shutdown_event = shutdown_event

    def run(self):
        # Repeat until graceful_shutdown
        while not self.shutdown_event.is_set():
            # Get pending job
            try:
                task = self.task_queue.get(timeout=1)  # Wait for a task for 1 second
            except queue.Empty:
                continue  # If no task is available, check again
            # Execute the job and save the result to disk
            job_id, result = self._execute_task(task)
            filename = os.path.join(self.results_dir, f"{job_id}.json")

            with open(filename, 'w') as f:
                json.dump(result, f)

            print(f"File '{filename} created successfully")

    @staticmethod
    def _execute_task(task):
        (job_id, compute_function, *args) = task
        result = compute_function(*args)
        return job_id, result
