from app.trader.maker import Maker
from apscheduler.schedulers.background import BlockingScheduler

BAT_KEY = "BAT_KEY"
BAT_SECRET = "BAT_SEC"

if __name__ == '__main__':

    maker = Maker("BAT_USDT", "BAT", BAT_KEY, BAT_SECRET, 10000, times=100)

    scheduler = BlockingScheduler(timezone='Asia/Shanghai')
    scheduler.add_job(maker.auto_bid, 'interval', seconds=4, max_instances=1)
    scheduler.add_job(maker.auto_bid_faster, 'interval', seconds=3, max_instances=1)
    scheduler.start()