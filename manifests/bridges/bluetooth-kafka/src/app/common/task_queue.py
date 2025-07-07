import queue
import logging
import asyncio

task_queue = queue.Queue()  

def add_task(task, *args, **kwargs): 
    task_queue.put((task, args, kwargs))
    logging.info(f"Added Bluetooth task to queue: {task} args={args} kwargs={kwargs}")

def start_queue_worker():
    async def worker():
        while True:
            task, args, kwargs = task_queue.get()
            if task is None:
                break
            try:
                logging.debug(f"Processing Bluetooth task: {task} args={args} kwargs={kwargs}")
                result = task(*args, **kwargs)
                if asyncio.iscoroutine(result):
                    logging.debug("Task is a coroutine, awaiting result...")
                    await result
                    logging.debug("Coroutine task completed.")
            except Exception as e:
                logging.error(f"Bluetooth task failed: {e}")
            finally:
                task_queue.task_done()
            
    import threading
    worker_thread = threading.Thread(target=lambda: asyncio.run(worker()))
    worker_thread.daemon = True  # Daemonize thread
    worker_thread.start()
    logging.info("Bluetooth worker thread started.")
 

def stop_queue_worker():
    task_queue.put(None)
    logging.info("Sentinel added to queue to stop Bluetooth worker.")
 