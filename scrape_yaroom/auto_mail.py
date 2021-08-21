import smtplib
from email.message import EmailMessage
from datetime import datetime, date, timedelta
from pytz import timezone
from seleYaroom import YaroomScrap
import json



def getfreeRooms(reservDic):
    freeRoomDic = dict()

    for building in reservDic:
        reservs = reservDic[building]
        tmpLst = list()
        for room,inf in reservs.items():
            if(not inf):
                tmpLst.append(room)
            elif( (len(inf) == 1) and (inf['time'] == "00:00 - midnight")):
                tmpLst.append(room)

        freeRoomDic[building] = tmpLst

    return freeRoomDic
                

def main():
    tz2 = timezone('Asia/Shanghai')
    dt2 = datetime.now(tz=tz2)
    weekdayIdx = (dt2.weekday())
    # print(dt2)

    Scraper = YaroomScrap()
    Scraper.standardScrape(weekdayIdx - 2) # 4 should be thursday 
    reserv = Scraper.getReservations()
    freeDic = getfreeRooms(reserv)

    msg = EmailMessage()
    content = "Hi there this is Alex. \n"
    content.append(json.dumps(freeDic, indent=4))

    msg.set_content(content)
    msg['Subject'] = 'Free Rooms Status'
    msg['From'] = 'Alex Jin'
    msg['To'] = 'zj61@duke.edu'
    print(msg)

    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()

if __name__ == '__main__':
    main()