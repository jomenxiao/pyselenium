# -*- coding: utf-8 -*-  

from selenium import webdriver
import os
import re
import json
import time



#const
PngDir = "./SnapshotDir"
BaseHTTP = "http://192.168.2.188:3000"
LoginURL = "/login"
UserName = "admin"
PassWord = "admin"
#http://192.168.2.188:3000/api/search?query=
dashboardURL = "/api/search?query="

panelURL = "/api/annotations?limit=10000"

FromTime = 1510535835702
ToTime = 1511075844572


loginButton = '//button[@type="submit"]'



#http://192.168.2.188:3000/api/annotations?limit=10000
#http://192.168.2.188:3000/dashboard/db/test-cluster-disk-performance?orgId=1&from=1510166419415&to=1511073638636
#http://192.168.2.188:3000/dashboard/db/test-cluster-tidb?&from=1510166419415&to=1511073638636
#http://192.168.2.188:3000/dashboard/db/test-cluster-tidb?panelId=37&fullscreen&orgId=1&from=1510535835702&to=1511075844572&refresh=30s
#http://192.168.2.188:3000/dashboard/db/test-cluster-tidb?panelId=37&fullscreen&from=1510535835702&to=1511075844572
class GrafanaClient(object):

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.dashboradUrls = {}
        self.GetUrls = {}

    def savePng(self,filename):
        return self.driver.save_screenshot(os.path.join(PngDir,filename))


    def findElement(self,matchInfo):
        return self.driver.find_element_by_xpath(matchInfo)

    def loginGrafana(self):
        print "{}{}".format(BaseHTTP, LoginURL)
        self.driver.get("{}{}".format(BaseHTTP, LoginURL))
        username = self.driver.find_element_by_name('username')
        password = self.driver.find_element_by_name('password')
        username.send_keys(UserName)
        password.send_keys(PassWord)

        logButton = self.findElement('//button[@type="submit"]')
        logButton.click()
        self.savePng("login.png")

    def getDashboards(self):
        self.dashboradUrls = []
        print "{}{}".format(BaseHTTP, dashboardURL)
        self.driver.get("{}{}".format(BaseHTTP, dashboardURL))
        out = json.loads(re.findall(r"\[\{.*\}\]",self.driver.page_source)[0]) 
        for u in out:
            if u["uri"]:
                self.dashboradUrls.append("{}{}".format("/dashboard/", u["uri"]))
                # nameTab = u["title"].replace(" ","_")
                # shareUrl = self.getShareUrl("{}.png".format(nameTab), "{}{}{}?from={}&to={}".format(BaseHTTP, "/dashboard/", u["uri"],FromTime,ToTime))
                # print "{}  {}".format(nameTab, shareUrl)
                

    def getPanels(self):
        self.driver.get("{}{}".format(BaseHTTP, panelURL))
        out = json.loads(re.findall(r"\[\{.*\}\]",self.driver.page_source)[0]) 
        for p in out:
            if p["panelId"]:
                for u in self.dashboradUrls:
                    nameTab = p["title"].replace(" ","_")
                    print "{}{}?panelId={}&from={}&to={}&fullscreen".format(BaseHTTP,u,p["panelId"], FromTime,ToTime)
                    shareUrl = self.getShareUrl("{}.png".format(nameTab), "{}{}?panelId={}&from={}&to={}&fullscreen".format(BaseHTTP,u,p["panelId"], FromTime,ToTime))
                    print "{}  {}".format(nameTab, shareUrl)


    def getShareUrl(self,pngName, url):
        self.driver.get(url)
        time.sleep(3)
        self.savePng(pngName)
        for i in range(3):
            try:
                shareIcon = self.findElement('//a[@bs-tooltip="\'Share dashboard\'"]')
                shareIcon.click()
                break
            except Exception as e:
                if i == 2:
                    raise e
                time.sleep(3)

        for i in range(3):
            try:
                snapshotTab = self.findElement('//i[@class="icon-gf icon-gf-snapshot"]')
                snapshotTab.click()
                break
            except Exception as e:
                if i == 2:
                    raise e
                time.sleep(3)

        for i in range(3):
            try:
                externalEnabledButton = self.findElement('//button[@ng-if="externalEnabled"]')
                externalEnabledButton.click()
                break
            except Exception as e:
                if i == 2:
                    raise e
                time.sleep(3)


        for i in range(3):
            try:
                shareUrl = self.findElement('//a[@class="large share-modal-link"]')
                break
            except Exception as e:
                if i == 2:
                    raise e
                time.sleep(5)
        

        return shareUrl.text

def init():
    pass


def main():
    print "start..."

    if not os.path.exists(PngDir):
        os.makedirs(PngDir)

    init()

    r = GrafanaClient()
    r.loginGrafana()
    r.getDashboards()
    r.getPanels()





if __name__ == '__main__':
    main()
