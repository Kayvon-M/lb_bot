from datetime import datetime, timedelta
import sys
import os
import asyncio
import threading
import discord

# from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def say_hello_with_time_passed(time_passed):
    print('Hello, the time passed is: {0} minutes'.format(time_passed))

class SchedulerService:
    def __init__(self):
        # self.client = discord.Client()
        self.lbSchedulerDB = "lbScheduler"
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_jobstore('mongodb', collection=self.lbSchedulerDB, database="1v1lb")
        # self.run_after_1_min(say_hello_with_time_passed, args=[1])
        # self.scheduler.add_job(say_hello_with_time_passed, 'interval', minutes=1, args=[1])
        self.scheduler.start()

        # try:
        #     asyncio.get_event_loop().run_forever()
        # except (KeyboardInterrupt, SystemExit):
        #     pass
        t = threading.Thread(target=self.loop_in_thread, args=(asyncio.get_event_loop(),))
        t.start()

    def loop_in_thread(self, loop=None):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def add_job(self, func, trigger, run_date=None, args=None):
        self.scheduler.add_job(func, trigger, run_date=run_date, args=args)

    def remove_job(self, job_id):
        self.scheduler.remove_job(job_id)

    def get_jobs(self):
        return self.scheduler.get_jobs()
    
    def get_job(self, job_id):
        return self.scheduler.get_job(job_id)
    
    def get_job_ids(self):
        return self.scheduler.get_job_ids()
    
    def get_job_id(self, job):
        return self.scheduler.get_job_id(job)
    
    def clear(self):
        self.scheduler.remove_all_jobs()

    def run_after_1_min(self, func, args=None):
        run_date = datetime.now() + timedelta(minutes=1)
        self.add_job(func, 'date', run_date=run_date, args=args)

    def delete_challenge_tc_job(self, channel):
        run_date = datetime.now() + timedelta(minutes=1)
        self.add_job(channel.delete, 'date', run_date=run_date)

    def message_user_about_challenge_job(self, funcOne, funcTwo, funcThree, argsOne=None, argsTwo=None, argsThree=None):
        run_date = datetime.now() + timedelta(days=1)
        self.add_job(funcOne, 'date', run_date=run_date, args=argsOne)
        run_date = datetime.now() + timedelta(days=2)
        self.add_job(funcTwo, 'date', run_date=run_date, args=argsTwo)
        run_date = datetime.now() + timedelta(days=2, hours=23)
        self.add_job(funcThree, 'date', run_date=run_date, args=argsThree)