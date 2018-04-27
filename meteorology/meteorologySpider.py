# -*- coding: utf-8 -*-
import os
from threading import Timer
from lxml import etree
import requests
from selenium import webdriver
import time
from selenium.webdriver.firefox.options import Options
from interfaceSpider.meteorology.getini import Ini

class meteSpider:

    def __init__(self):
        self.headers = {
            "Referer": "http://data.cma.cn/",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3067.6 Safari/537.36",
            }

        self.filePath = Ini().getConfigValue('download', 'namePath')
        print self.filePath

    def main(self):
        """
        main函数
        :rtype : object
        """

        ts = [1, 3, 4, 6, 7]  # ----- {2-7,9-12},{14},{15},{16,17},{19-23,25-31}
        for t in ts:
            url = 'http://data.cma.cn/data/online.html?t={t}'.format(t=t)
            urlImgList_type = self.selenium_js(url)
            self.downImg(urlImgList_type)

        Timer(5*60, self.main).start()

    def selenium_js(self, url):
        """
        模拟浏览器访问网站
        :param url:需要访问的网站url
        :return:图片下载url列表
        """
        if url != '':
            print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), "PhantomJS is starting..."
            # driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'], executable_path='C:\Python27\Scripts\phantomjs') #指定使用的浏览器
            # driver = webdriver.Firefox()  # executable_path='geckodriver'

            options = Options()
            options.add_argument('-headless')
            driver = webdriver.Firefox(firefox_options=options)  # executable_path='geckodriver'

            try:
                print("访问"+url)
                # 5种类型下 各种类型的气象
                mete_list = self.easyuiTree(url)
                print mete_list

                urlImg_list = []
                for tree_num in mete_list[0]:

                    driver.get(url)
                    time.sleep(1)
                    # # 将页面拉至最底端
                    # js = "var q=document.documentElement.scrollTop=10000"
                    # driver.execute_script(js)
                    # time.sleep(1)

                    # 获取气象数据
                    easyui_tree = '//div[@id="_easyui_tree_{num}"]'.format(num=tree_num)
                    print easyui_tree
                    driver.find_element_by_xpath(easyui_tree).click()
                    time.sleep(1)

                    # 获取最新气象数据
                    driver.find_element_by_xpath('//a[@id="btn"][1]').click()
                    time.sleep(2)
                    # print driver.is_displayed()

                    body = driver.page_source
                    body = etree.HTML(body)
                    image_url = body.xpath("//tr[@id='tablerow3Image']/td/img[@id='showimages']/@src")[0]
                    print 'image_urls:', image_url
                    urlImg_list.append(image_url)
                urlImg_type_list = [urlImg_list, mete_list[1]]
                return urlImg_type_list
            finally:
                driver.close()
                print"PhantomJS is closed"
        else:
            return

    def easyuiTree(self, url):
        t = int(url.split('=')[-1])
        mete_list = []
        if 1 == t:
            easyui_tree_list = [x for x in range(2, 13) if x != 8]
            mete_list = [easyui_tree_list, 'type_1']
        elif 3 == t:
            easyui_tree_list = [14]
            mete_list = [easyui_tree_list, 'type_2']
        elif 4 == t:
            easyui_tree_list = [15]
            mete_list = [easyui_tree_list, 'type_3']
        elif 6 == t:
            easyui_tree_list = [16, 17]
            mete_list = [easyui_tree_list, 'type_4']
        elif 7 == t:
            easyui_tree_list = [x for x in range(19, 32) if x != 24]
            mete_list = [easyui_tree_list, 'type_5']
        return mete_list

    def downImg(self, urlImgList_type):
        """
        下载图片
        :param image_url:图片下载url列表
        """
        path = ''
        timeDate = time.strftime('%Y%m%d', time.localtime(time.time()))

        if urlImgList_type[1] == 'type_1':
            path = self.filePath + '\\Ground_observation\\' + timeDate
        elif urlImgList_type[1] == 'type_2':
            path = self.filePath + '\\Satellite_Images\\' + timeDate
        elif urlImgList_type[1] == 'type_3':
            path = self.filePath + '\\Radar\\' + timeDate
        elif urlImgList_type[1] == 'type_4':
            path = self.filePath + '\\Precipitation_fusion\\' + timeDate
        elif urlImgList_type[1] == 'type_5':
            path = self.filePath + '\\Ground_Assimilation\\' + timeDate

        for image_url in urlImgList_type[0]:
            image_url = image_url.strip()
            print '正在下载：', image_url
            img = requests.get(image_url, headers=self.headers)
            time.sleep(0.5)
            imgName = image_url.split('/')[-1]  # 图片命名
            # 文件路径不存在，则创建
            if not os.path.isdir(path):
                os.makedirs(path)
            fileName = path + "\\{name}".format(name=imgName)
            # 图片存入文件夹
            with open(fileName, 'wb') as f:
                f.write(img.content)

if __name__ == '__main__':
    spider = meteSpider()
    spider.main()


