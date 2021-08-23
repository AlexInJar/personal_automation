import smtplib
from email.message import EmailMessage
from datetime import datetime, date, timedelta
from pytz import timezone
from seleYaroom import YaroomScrap
import json
from apscheduler.schedulers.blocking import BlockingScheduler



def getfreeRooms(reservDic):
    freeRoomDic = dict()

    for building in reservDic:
        reservs = reservDic[building]
        tmpLst = list()
        for room,inf in reservs.items():
            if(not inf):
                tmpLst.append(room)
            elif( (len(inf) == 1) and (inf[0]['time'] == "00:00 - midnight")):
                tmpLst.append('*{}'.format(room))

        freeRoomDic[building] = "--".join(tmpLst)

    return freeRoomDic

def getScrapedResults():
    tz2 = timezone('Asia/Shanghai')
    dt2 = datetime.now(tz=tz2)
    weekdayIdx = (dt2.weekday())
    # print(dt2)

    Scraper = YaroomScrap()
    Scraper.standardScrape(weekdayIdx + 1) # 4 should be thursday 
    reserv = Scraper.getReservations()
    with open('jsons/{}.json'.format(dt2.date()), 'w') as fp:
        json.dump(reserv, fp, sort_keys= True, indent=4)
    return reserv
      
def main0():
    scrape_result = getScrapedResults()
    content = '''Todays reservation: \n \n {}'''.format(json.dumps(scrape_result, indent=4))
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = 'Free Rooms Status'
    msg['From'] = 'Alex Jin'
    msg['To'] = 'zj61@duke.edu'
    print(msg)

    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()
    

def main():
    tz2 = timezone('Asia/Shanghai')
    dt2 = datetime.now(tz=tz2)
    weekdayIdx = (dt2.weekday())
    # print(dt2)

    Scraper = YaroomScrap()
    Scraper.standardScrape(weekdayIdx - 2) # 4 should be thursday 
    reserv = Scraper.getReservations()
    with open('jsons/{}.json'.format(dt2), 'w') as fp:
        json.dump(reserv, fp, sort_keys= True, indent=4)
    freeDic = getfreeRooms(reserv)

    msg = EmailMessage()
    content = "Here is the tmr that are free.\n{}".format(json.dumps(freeDic, indent=4))
    # content.append(json.dumps(freeDic, indent=4))

    msg.set_content(content)
    msg['Subject'] = 'Free Rooms Status'
    msg['From'] = 'Alex Jin'
    msg['To'] = 'zj61@duke.edu'
    print(msg)

    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()

if __name__ == '__main__':
    sched = BlockingScheduler()

    # Runs from Monday to Friday at 5:30 (am) until
    sched.add_job(main0, 'cron', day_of_week='mon-fri', hour=6, minute=10)
    sched.start()
    # getScrapedResults()
