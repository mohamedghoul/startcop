from apscheduler.schedulers.background import BackgroundScheduler
from src.knowledge_base.qcb_scraper import QCBKnowledgeBaseScraper
import asyncio, os
from datetime import datetime


async def refresh_kb():
    scraper = QCBKnowledgeBaseScraper()
    regs = scraper.scrape_all_regulations()
    scraper.save_knowledge_base(
        regs, filename=os.getenv("KB_PATH", "real_qcb_regulations.json")
    )
    print("KB refreshed at", datetime.now())


def start_scheduler():
    sched = BackgroundScheduler()
    sched.add_job(lambda: asyncio.run(refresh_kb()), "interval", hours=24)
    sched.start()
    # No need to run event loop in background thread
