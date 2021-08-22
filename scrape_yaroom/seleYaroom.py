from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
import time
import json

class YaroomScrap(object):
    def __init__(self) -> None:
        super().__init__()
        opts = ChromeOptions()
        opts.add_argument("--headless")
        opts.add_argument("window-size=1400,600")
        self.driver = webdriver.Chrome(options=opts)
        self.driver.set_window_size(1920, 1080)
        self.roomdic = {
            'AB':16959,
            'CC':16960,
            'IB':36669
        }
        self.wait = WebDriverWait(self.driver,10)
        self.reservations = dict()
        # print(self.driver.page_source)

    def loginGuest(self):
        self.driver.get(r'https://dku.yarooms.com/account/login?return=https:%2F%2Fdku.yarooms.com%2Fschedule%2Fweekly%3Flocation%3D16959')
        self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR,r'#wrapper > div.content > div > div:nth-child(1) > div.login-right > form > a > span'))
        ).click()
        time.sleep(10)

    def ScrapeRoom(self, Room, numWeek):
        self.driver.get('https://dku.yarooms.com/schedule/weekly?location={}'.format(self.roomdic[Room]))
        avail_dic = dict()
        for i in range(2):

            table = self.wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR,r'#content'))
            )

            time.sleep(30)
            relativeDiv = table.find_element_by_css_selector(r'div.tleft.weekly').find_element_by_css_selector(r'div.relative')
            rowRooms = relativeDiv.find_elements_by_css_selector(r'div.trow.room')
            # print(relativeDiv.get_attribute('innerHTML'))

            roomLst = [rowRoom.find_element_by_css_selector(r'div.name').get_attribute('title') for rowRoom in rowRooms ]
            roomNum = len(roomLst)
            lftTable = table.find_element_by_css_selector(r'div.tright.weekly.expanded')
            divRs = lftTable.find_elements_by_css_selector(r'div:not(.heading-row) div.trow')
            for i in range(roomNum + 1):
                print(i)
                if (i == 0):
                    continue
                divCell = divRs[i].find_elements_by_css_selector(r'div.cell')[numWeek - 1]
                print(divCell.find_elements_by_css_selector('span.no.faded'))
                # print(divCell.get_attribute('innerHTML'))
                if( divCell.find_elements_by_css_selector('span.no.faded') ):
                    avail_dic[roomLst[i-1]] = None
                else:
                    # time.sleep(5)
                    divSchedule = divCell.find_element_by_css_selector(r'div.schedule-meetings')
                    print(divSchedule.get_attribute('innerHTML'))
                    bookaLst = divSchedule.find_elements_by_css_selector(r'a')
                    # .get_attribute('ya-tooltip').split("<br>")
                    infLst = [a.get_attribute('ya-tooltip').split("<br>") for a in bookaLst]
                    avail_dic[roomLst[i-1]] = [{
                        'reserver' : inf[0],
                        'time' : inf[1]
                    } for inf in infLst]

            # parsed = json.loads(avail_dic)
            # print(json.dumps(avail_dic, indent=4, sort_keys= False))

            if((Room == 'CC') or (i == 1)):
                break
            else:
                time.sleep(10)
                self.wait.until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR,r'#pageView2 > a'))
                ).click()

        self.reservations[Room] = avail_dic

    def standardScrape(self,numWeek):
        self.loginGuest()
        self.ScrapeRoom('AB',numWeek)
        self.ScrapeRoom('CC',numWeek)
        self.ScrapeRoom('IB',numWeek)

    def getReservations(self):
        return self.reservations

        


def main():
    scraper = YaroomScrap()
    # scraper.loginGuest()
    # scraper.ScrapeRoom('AB',4)
    scraper.standardScrape(4)
    time.sleep(10)

if __name__ == '__main__' :
    main()