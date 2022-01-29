from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC #期望的条件
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import datetime
from time import sleep
import json
import requests
from urllib.parse import urlencode

class Qiangpiao(object):
     #初始化函数
     def __init__(self,from_station,to_station,depart_time,train_num,passenger):
         self.login_url = 'https://kyfw.12306.cn/otn/resources/login.html'
         self.initmy_url = 'https://kyfw.12306.cn/otn/view/index.html'
         self.search_url = 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc'
         self.confirmPassenger = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
         self.driver = webdriver.Chrome(r"C:\Users\Administrator\AppData\Local\Google\Chrome\Application\chromedriver.exe")
         self.from_station = from_station
         self.to_station = to_station
         self.depart_time = depart_time
         self.train_num = train_num
         self.passenger = passenger
         self.now_month = datetime.date.today().month
         self.noe_day = datetime.date.today().day
         self.leave_month = int(self.depart_time.split('-')[1])
         self.leave_day = int(self.depart_time.split('-')[2])

     #_login只想在类中调用
     def _login(self):
         self.driver.get(self.login_url)
         xpath = '/html/body/div[1]/div[2]/div[2]/ul/li[2]'
         self.driver.find_element(By.XPATH,xpath).click()
         WebDriverWait(self.driver,1000).until(EC.url_to_be(self.initmy_url))
         print('恭喜您，您已登录成功了！')

     def _order_ticket(self):
         # 1、跳转到查余票的界面
         self.driver.get(self.search_url)
         # 出发地输入
         self.driver.find_element(By.ID, "fromStationText").click()
         self.driver.find_element(By.ID, "fromStationText").send_keys(self.from_station)
         self.driver.find_element(By.ID, "fromStationText").send_keys(Keys.ENTER)
         # 2、等待出发地是否输入正确
         WebDriverWait(self.driver, 1000).until(
             EC.text_to_be_present_in_element_value((By.ID, "fromStationText"), self.from_station))
         # 目的地输入
         self.driver.find_element(By.ID, "toStationText").click()
         self.driver.find_element(By.ID, "toStationText").send_keys(self.to_station)
         self.driver.find_element(By.ID, "toStationText").send_keys(Keys.ENTER)
         # 3、等待目的地是都输入正确
         WebDriverWait(self.driver, 1000).until(
             EC.text_to_be_present_in_element_value((By.ID, "toStationText"), self.to_station))
         # 等待只能预定从当日起15日之后的车票，所以将对时间的范围的限定
         try:
             # 出发日期输入
             self.driver.find_element(By.ID, "train_date").clear()
             self.driver.find_element(By.ID, "train_date").click()
             self.driver.find_element(By.ID, "train_date").send_keys(self.depart_time)
             self.driver.find_element(By.ID, "train_date").send_keys(Keys.ENTER)
         except Exception:
             print("您输入日期的格式不正确或者日期")
         # 4、等待出发日期是否输入正确
         WebDriverWait(self.driver, 1000).until(
             EC.text_to_be_present_in_element_value((By.ID, "train_date"), self.depart_time))
         flag = 0
         #开始进行相应的刷票操作（若有票则直接下单，若无票则可以进行循环的抢票）
         while True:
             # 5、等待查询按钮是否可用
             WebDriverWait(self.driver, 1000).until(EC.element_to_be_clickable((By.ID, "query_ticket")))
             # 6、如果可以点击找到查询按钮执行点击事件
             searchBotton = self.driver.find_element(By.ID, "query_ticket")
             searchBotton.click()
             # 7、点击查询按钮之后等待车票信息页面被加载完成
             WebDriverWait(self.driver, 1000).until(
                 EC.presence_of_element_located((By.XPATH, ".//tbody[@id = 'queryLeftTable']/tr")))
             # 8、找到所有没有datatrain属性的tr标签
             tr_list = self.driver.find_elements(By.XPATH, ".//tbody[@id ='queryLeftTable']/tr[not(@datatran)]")
             # 9、遍历所有满足条件的tr标签
             for tr in tr_list:
                 train_number = tr.find_element(By.CLASS_NAME, 'number').text
                 if train_number in self.train_num:
                     #动车的二等座
                     left_ticket = tr.find_element(By.XPATH, './/td[3]').text  # 找到第四个td标签下的文本
                     #普通火车的硬卧
                     left_ticket1 = tr.find_element(By.XPATH, './/td[7]').text
                     #普通火车的硬座
                     #left_ficket2 = tr.find_element(By.XPATH, './/td[9]').text
                     if (left_ticket == '有' or left_ticket.isdigit) or (
                             left_ticket1 == '有' or left_ticket1.isdigit):  # 判断输入的车次是否在列表中
                         orderBotton = tr.find_element_by_class_name('btn72')
                         orderBotton.click()
                         # 等待是否来到乘客确认页面
                         WebDriverWait(self.driver, 1000).until(EC.url_to_be(self.confirmPassenger))
                         # 等待所有的乘客信息被加载完毕
                         WebDriverWait(self.driver, 1000).until(EC.presence_of_element_located((By.XPATH, ".//ul[@id = 'normal_passenger_id']/li")))
                         # 获取所有的乘客信息
                         passanger_labels = self.driver.find_elements(By.XPATH,
                                                                      ".//ul[@id = 'normal_passenger_id']/li/label")
                         for passanger_label in passanger_labels:  # 遍历所有的label标签
                             name = passanger_label.text
                             if name in self.passenger:  # 判断名字是否与之前输入的名字重合
                                 passanger_label.click()  # 执行点击操作

                                 # 获取提交订单的按钮
                                 submitBotton = self.driver.find_element(By.ID, 'submitOrder_id')
                                 submitBotton.click()
                                 # 显示等待确人订单对话框是否出现
                                 WebDriverWait(self.driver, 1000).until(
                                     EC.presence_of_element_located((By.CLASS_NAME, 'dhtmlx_wins_body_outer')))
                                 # 显示等待确认按钮是否加载出现，出现后执行点击操作
                                 WebDriverWait(self.driver, 1000).until(
                                     EC.presence_of_element_located((By.ID, 'qr_submit_id')))
                                 ConBotton = self.driver.find_element(By.ID, 'qr_submit_id')
                                 ConBotton.click()
                                 flag = 1
                 if flag == 1:
                    break

             if EC.url_to_be(self.confirmPassenger):
                 break
             sleep(2)

     def run(self):
         self._login()
         self._order_ticket()


class Check():
    def __init__(self, date, start, end, purpose):
        self.base_url = 'https://kyfw.12306.cn/otn/leftTicket/queryA?'
        self.url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9018'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            'Cookie': 'JSESSIONID=B709F9775E72BDED99B2EEBB8CA7FBB9; BIGipServerotn=1910046986.24610.0000; RAIL_EXPIRATION=1579188884851; RAIL_DEVIC'
        }
        self.date = date
        self.start_station = start
        self.end_station = end
        self.purpose = purpose if purpose == 'ADULT' else '0X00'

    #查找车站的中文简称，用于构造cookie,完成余票的查询链接
    def look_station(self):
        try:
            with open('station_code.json', 'r') as f:
                dic = json.load(f)#将json字符串转化为python对象
        except FileNotFoundError:
            response = requests.get(self.url).text
            station = response.split('@')[1:]
            dic = {}
            for each in station:
                i = each.split('|')
                dic[i[1]] = i[2]
            with open('station_code.json','w') as f:
                f.write(json.dumps(dic))
                #也可以用json.dump()来直接写入文件中（将python对象转化为json字符串）
        return [dic[self.start_station], dic[self.end_station]]

    def get_info(self, start_end):
        date = {
            'leftTicketDTO.train_date': self.date,
            'leftTicketDTO.from_station': start_end[0],
            'leftTicketDTO.to_station': start_end[1],
            'purpose_codes': self.purpose,
        }
        url = self.base_url + urlencode(date)
        # print("完整的余票查询链接：",url)

        count = 0
        # while count == 0:
        #     print("余票查询中... %d次" %check_count)
        response = requests.get(url, headers = self.headers)
        try:
            json = response.json()
        except ValueError:
            print("余票查询有误，请仔细的检查所输入的内容，以及日期是否在规定的范围之内")
            return
        map = json['data']['map']
        maps = json['data']['result']
        # print(map)
        # print(maps)
        for each in maps:
            # print(each+'/n')
            s = each.split('|')[3:]
            info = {
                '车次' : s[0],
                '出发-到达' : map[s[3]] + '-' + map[s[4]],
                '时间': s[5] + '-' + s[6],
                '历时': s[7],
                '二等座': s[27],
                '一等座': s[28],
                '商务座': s[29],
                '软卧一等卧': s[20],
                '硬卧二等卧': s[25],
                '硬座': s[26],
            }
            print(info)


if __name__ == '__main__':
    while True:
        print("请输入’查询‘ , ’购票‘ 或者 ’结束‘")
        select = input()
        if select == '查询':
            date = input('请输入出发的日期：（格式为Y-M-d）')
            start_station = input('请输入出发地：')
            end_station = input('请输入目的地：')
            c = Check(date, start_station, end_station, 'ADULT')
            start_end = c.look_station()
            c.get_info(start_end)
        elif select == '购票':
            from_station = input('请输入出发地：')
            to_station = input('请输入目的地：')
            depart_time = input('出发时间：（格式为Y-M-d）')
            # depart_time = '2022-01-28'
            passengers = input('乘客姓名：（如有多个乘客使用英文逗号分割）').split(',')
            # passengers = '董昊'
            trains = input('车次：（如有多个车次使用英文逗号分割）').split(',')
            # trains = 'K4032'
            spider = Qiangpiao(from_station, to_station, depart_time, trains, passengers)
            spider.run()
        else:
            print('请仔细的检查要求填写的内容，程序无法执行')
            break


