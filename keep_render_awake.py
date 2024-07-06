import schedule
import time
import datetime
import requests

def keep_render_awake():
    current_time = datetime.datetime.now().time()
    if current_time < datetime.time(0, 0) or current_time >= datetime.time(7, 0):
        try:
            response = requests.get("https://linebot-21rc.onrender.com")
            if response.status_code == 200:
                print("Render is awake")
            else:
                print("Failed to wake up render")
        except Exception as e:
            print(f"Error while waking up render: {e}")
    else:
        print("Render is asleep")

# 設置每 10 分鐘喚醒一次
schedule.every(10).minutes.do(keep_render_awake)

while True:
    schedule.run_pending()
    time.sleep(1)
