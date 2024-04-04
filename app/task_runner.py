"""
Provides a ThreadPool class for managing asynchronous task execution.
"""

import os
import pickle
import queue
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
        self.encountered_tasks = []
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
        self.encountered_tasks.append(task[0])

    def shutdown(self):
        """
        Initiates a graceful shutdown of the thread pool.

        - Signals worker threads to stop accepting new tasks.
        - Waits for all pending tasks to complete.
        - Joins worker threads to ensure proper termination.
        """
        self.shutdown_event.set()
        for task_runner in self.task_runners:
            task_runner.join()

    def update_results_dir(self, results_dir):
        """
        Updates the results directory for the thread pool and its task runners.
        """
        self.results_dir = results_dir
        for task_runner in self.task_runners:
            task_runner.results_dir = results_dir

    def is_shutting_down(self):
        """
        Checks if the thread pool is currently undergoing shutdown.
        """
        return self.shutdown_event.is_set()


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
        while True:
            # Stop if graceful_shutdown and there are no tasks to poll
            if self.shutdown_event.is_set() and self.task_queue.empty():
                return
            try:
                # Get pending job
                task = self.task_queue.get(timeout=1)  # Wait for a task for 1 second
            except queue.Empty:
                continue  # If no task is available, check again
            # Execute the job and save the result to disk
            job_id, result = self._execute_task(task)
            filename = os.path.join(self.results_dir, f"{job_id}.pkl")

            with open(filename, 'wb') as job_file:
                pickle.dump(result, job_file)

    @staticmethod
    def _execute_task(task):
        (job_id, compute_function, *args) = task
        result = compute_function(*args)
        return job_id, result
