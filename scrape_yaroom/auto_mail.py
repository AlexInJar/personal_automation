import smtplib
from email.message import EmailMessage
from tabulate import tabulate
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, date, timedelta
from pytz import timezone
from seleYaroom import YaroomScrap
import json
from apscheduler.schedulers.blocking import BlockingScheduler
import pandas as pd

text = """
Hello, Friend.

Here is your data:
AB: \n
{tableAB}
CC: \n
{tableCC}
IB: \n
{tableIB}

Regards,

Me"""

html = """
<html><body><p>Hello, Friend.</p>
<p>Here is your data:</p>
AB: \n
{tableAB}
CC: \n
{tableCC}
IB: \n
{tableIB}

<p>Regards,</p>
<p>Me</p>
</body></html>
"""



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
    text = """
    Hello, Friend.

    Reservation today:
    AB: \n
    {tableAB}
    CC: \n
    {tableCC}
    IB: \n
    {tableIB}

    Regards,

    Me"""

    html = """
    <html><body><p>Hello, Friend.</p>
    <p>Reseravation today:</p>
    AB: \n
    {tableAB}
    CC: \n
    {tableCC}
    IB: \n
    {tableIB}

    <p>Regards,</p>
    <p>Me</p>
    </body></html>
    """

    scrape_result = getScrapedResults()
    # with open('jsons/2021-08-22.json','r') as f:
    #     scrape_result = json.loads(f.read())
    buid_dic = dict()
    for building,reservation in scrape_result.items():
        buid_dic[building] = {
            room : '\n\n\n'.join(["{}\t\t{}".format(bookDic['reserver'],bookDic['time']) for bookDic in booking]) if bool(booking) else '\n' for room, booking in reservation.items()
        }
    dfAB, dfCC, dfIB = pd.DataFrame([buid_dic['AB']]).transpose(), pd.DataFrame([buid_dic['CC']]).transpose(), pd.DataFrame([buid_dic['IB']]).transpose()
    # print(tabulate(dfAB))
    txtAB, txtCC, txtIB = tabulate(dfAB, headers="firstrow", tablefmt="grid"),tabulate(dfIB, headers="firstrow", tablefmt="grid"),tabulate(dfCC, headers="firstrow", tablefmt="grid")
    htmlAB, htmlCC, htmlIB = tabulate(dfAB, headers="firstrow", tablefmt="html"),tabulate(dfIB, headers="firstrow", tablefmt="html"),tabulate(dfCC, headers="firstrow", tablefmt="html")
    text = text.format(txtAB, txtCC, txtIB)
    html = html.format(htmlAB, htmlCC, htmlIB)
    msg = MIMEMultipart(
    "alternative", None, [MIMEText(text), MIMEText(html,'html')])

    # content = '''Todays reservation: \n \n {}'''.format(json.dumps(scrape_result, indent=4))
    # msg = EmailMessage()
    # msg.set_content(content)
    msg['Subject'] = 'Free Rooms Status'
    msg['From'] = 'lf180@duke.edu'
    msg['To'] = 'zj61@duke.edu'
    # print(msg)

    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()


    msg['From'] = 'xs90@duke.edu'
    msg['To'] = 'xs90@duke.edu'
    # print(msg)

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
    # main0()
    sched = BlockingScheduler()

    # Runs from Monday to Friday at 5:30 (am) until
    sched.add_job(main0, 'cron', day_of_week='mon-fri', hour=6, minute=10)
    sched.start()
    getScrapedResults()
