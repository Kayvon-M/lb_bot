from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

async def job():
    print("Hello World")


scheduler = AsyncIOScheduler()
scheduler.add_jobstore('mongodb', collection="lbScheduler", database="1v1lb")
scheduler.add_job(job, "interval", seconds=3)

scheduler.start()

try:
   asyncio.get_event_loop().run_forever()
except (KeyboardInterrupt, SystemExit):
    pass