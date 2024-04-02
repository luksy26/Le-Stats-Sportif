import os
import queue
import threading
import time
from threading import Thread


class ThreadPool:
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
        self.result_queue = queue.Queue()
        self.shutdown_event = threading.Event()
        self.task_runners = []

        # Create and start TaskRunner threads
        for _ in range(self.num_threads):
            task_runner = TaskRunner(self.task_queue, self.result_queue, self.shutdown_event)
            task_runner.start()
            self.task_runners.append(task_runner)

    def submit(self, task, *args, **kwargs):
        self.task_queue.put((task, args, kwargs))

    def shutdown(self):
        self.shutdown_event.set()
        # Wait for tasks to finish before joining threads
        self.wait_for_completion()
        for task_runner in self.task_runners:
            task_runner.join()

    def wait_for_completion(self):
        while not self.task_queue.empty():
            time.sleep(0.1)  # Short wait to avoid busy waiting


class TaskRunner(Thread):
    def __init__(self, task_queue, result_queue, shutdown_event):
        super().__init__()
        self.task_queue = task_queue
        self.result_queue = result_queue
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
            result = self._execute_task(*task)
            self.result_queue.put(result)
            self.task_queue.task_done()

    def _execute_task(self, func, args, kwargs):
        return func(*args, **kwargs)
