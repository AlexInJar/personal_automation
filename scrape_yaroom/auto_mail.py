import smtplib
from email.message import EmailMessage
from datetime import datetime, date, timedelta
from pytz import timezone

tz2 = timezone('Asia/Shanghai')
dt2 = datetime.now(tz=tz2)
print(dt2.weekday())
print(dt2)