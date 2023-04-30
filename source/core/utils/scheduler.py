from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import BaseJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor


class Scheduler:
    def __init__(self):
        self._scheduler = BackgroundScheduler()

    def add_job(self, func, trigger, **kwargs):
        self._scheduler.add_job(func, trigger, **kwargs)

    def start(self):
        self._scheduler.start()
