from threading import Thread
from typing import List, Literal
from queue import Queue
from .utils.debug_print import print_info, debug_print
import logging
from .constants import *
import atexit


class UploadWorker(Thread):
    state: Literal["running", "paused", "stopped"] = "running"

    def __init__(self, queue: Queue):
        Thread.__init__(self)
        self._queue = queue
        
    def run(self):
        while self.state == "running":
            data = self._queue.get(block=True)
            if data:
                self._send_to_keywords(data)
                self._queue.task_done()
    
    def pause(self):
        self.state = "paused"

    def _send_to_keywords(self, data):
        print_info(f"Sending data to KeywordsAI: {data}", print_func=debug_print)

        
class KeywordsAITaskQueue:
    
    _queue = Queue()
    _workers: List[UploadWorker] = []

    def __init__(self):
        for _ in range(KEYWORDSAI_NUM_THREADS):
            self._workers.append(UploadWorker(queue=self._queue))
        
        atexit.register(self.teardown)

    def initialize(self):
        for worker in self._workers:
            if not worker.is_alive():
                worker.start()
        return True

    def add_task(self, task_data):
        print_info(f"Adding task to queue: {task_data}", print_func=debug_print)
        self._queue.put(task_data, block=False)
    
    def flush(self):
        """Waiting until all the pending uploads in the queue are finished"""
        self._queue.join()

    def join(self):
        """
        Clear all tasks in the queue
        Blocks execution until finished
        """

        for worker in self._workers:
            # Avoid further accepting new uploads
            worker.pause()

        for worker in self._workers:
            try:
                worker.join()
            except RuntimeError:
                # consumer thread has not started
                pass

    def teardown(self):
        """Clear all the tasks in the queue and shutdown the workers"""

        self.flush()
        self.join()

        print_info("Shutdown success", print_func=logging.info)
        
        