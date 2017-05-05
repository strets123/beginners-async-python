import luigi
from time import sleep
class MyTask(luigi.Task):
    worker_timeout = 5
    def run(self):
        sleep(10)
        return luigi.LocalTarget("result", "done")    



