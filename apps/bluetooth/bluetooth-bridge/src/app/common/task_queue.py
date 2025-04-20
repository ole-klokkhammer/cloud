import queue
import logging
import asyncio

task_queue = queue.Queue()  

def add_task(task, *args, **kwargs): 
    task_queue.put((task, args, kwargs))
    logging.info(f"Added Bluetooth task to queue: {task} args={args} kwargs={kwargs}")

def start_queue_worker():
    def worker():
        while True:
            task, args, kwargs = task_queue.get()
            if task is None:
                break
            try:
                result = task(*args, **kwargs)
                if asyncio.iscoroutine(result):
                    asyncio.run(result)
            except Exception as e:
                logging.error(f"Bluetooth task failed: {e}")
            finally:
                task_queue.task_done()
            
    import threading
    worker_thread = threading.Thread(target=worker)
    worker_thread.daemon = True  # Daemonize thread
    worker_thread.start()
    logging.info("Bluetooth worker thread started.")
 

def stop_queue_worker():
    task_queue.put(None)
    logging.info("Sentinel added to queue to stop Bluetooth worker.")
 