from threading import Thread
from typing import List, Literal
from queue import Queue
import queue
from .utils.debug_print import print_info, debug_print, print_error
import logging
from .keywordsai_config import *
import atexit
from .client import KeywordsAIClient

class UploadWorker(Thread):
    state: Literal["running", "paused", "stopped"] = "running"

    def __init__(self, queue: Queue):
        Thread.__init__(self, daemon=True)
        self._queue = queue
        self._client = KeywordsAIClient()

    def _get_batch(self):
        batch = []
        while len(batch) < KEYWORDSAI_BATCH_SIZE:
            try:
                data = self._queue.get(block=False)
                if data:
                    batch.append(data)
            except queue.Empty:
                break
            except Exception as e:
                print_error(e, print_func=logging.error)
        return batch

    def _get_item(self):
        try:
            item = self._queue.get(block=False)
            return item
        except queue.Empty:
            return None

    def run(self):
        while self.state == "running":
            item = self._get_item()
            if not item:
                continue
            try:
                self._send_to_keywordsai(item)
            except Exception as e:
                print_error(e, print_func=logging.error)
            finally:
                self._queue.task_done()

    def pause(self):
        self.state = "paused"

    def _send_to_keywordsai(self, data):
        response = self._client.post(data)
        try:
            response_json = response.json()
            print_info(f"Response from KeywordsAI: {response_json}", print_func=debug_print)
        except Exception as e:
            print_error(e, print_func=logging.error)


class KeywordsAITaskQueue:

    _queue = Queue()
    _workers: List[UploadWorker] = []

    def __init__(self):
        self.initialize()
        atexit.register(self.join)

    def initialize(self):

        for _ in range(KEYWORDSAI_NUM_THREADS):
            worker = UploadWorker(self._queue)
            worker.start()
            self._workers.append(worker)
        return True

    def add_task(self, task_data):
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
            except Exception as e:
                print_error(e, print_func=logging.error)

    def teardown(self):
        """Clear all the tasks in the queue and shutdown the workers"""

        self.flush()
        self.join()

        print_info("Shutdown success", print_func=logging.info)
