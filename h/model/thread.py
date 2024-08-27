import concurrent.futures as pool
from multiprocessing import Process


class Thread:

    def __init__(self, process, job, params):
        self.process = process
        self.job = job
        self.params = params

    def run(self):
        self.process.start()

    def executor(self):
        with pool.ThreadPoolExecutor(max_workers=1) as e:
            e.submit(self.job, **self.params)
            e.shutdown()
