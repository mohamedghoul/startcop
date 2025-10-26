from apscheduler.schedulers.asyncio import AsyncIOScheduler
from knowledge_base.qcb_scraper import QCBKnowledgeBaseScraper
import asyncio, os
from datetime import datetime

async def refresh_kb():
    scraper = QCBKnowledgeBaseScraper()
    regs = scraper.scrape_all_regulations()
    scraper.save_knowledge_base(regs, filename=os.getenv("KB_PATH", "real_qcb_regulations.json"))
    print("KB refreshed at", datetime.now())

def start_scheduler():
    sched = AsyncIOScheduler()
    sched.add_job(refresh_kb, 'interval', hours=24)
    sched.start()
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass