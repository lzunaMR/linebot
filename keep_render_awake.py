import schedule
import time
import datetime
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def keep_render_awake():
    while True:
        current_time = datetime.datetime.now().time()
        if current_time < datetime.time(0, 0) or current_time >= datetime.time(7, 0):
            try:
                response = requests.get("https://linebot-db1b.onrender.com")
                if response.status_code == 200:
                    logger.info("Render is awake")
                else:
                    logger.info(f"Failed to wake up render: Status code {response.status_code}")
            except Exception as e:
                logger.error(f"Error while waking up render: {e}")
        else:
            logger.info("Render is asleep")

        # 等待10分鐘
        time.sleep(10 * 60)

if __name__ == "__main__":
    keep_render_awake()
