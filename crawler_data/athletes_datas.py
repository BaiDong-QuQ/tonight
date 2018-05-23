import requests
import re
import numpy as np
import csv
from tqdm import tqdm
from bs4 import BeautifulSoup


# 请求网页获取数据
def get_request(url):
    headers = {
        'User-Agent': 'Mozilla/5.0(WindowsNT10.0;WOW64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/68.0.3423.2Safari/537.36'
    }
    response = requests.get(url = url, headers = headers)
    # 中文编码出现问题，这里默认是‘ISO-8859-1’，需要改成‘utf8’
    response.encoding = 'utf8'
    response = response.text
    return response


# 得到运动员的个人链接
def get_athletes_url(response):
    soup = BeautifulSoup(response,'lxml')
    datas = soup.find_all(class_='logo')
    for data in datas:
        href = 'http://info.2016.163.com' + data.find('a')['href']
        yield href


# 获取运动员的信息
def get_detailinfo(href):
    url = href
    response = get_request(url)
    soup = BeautifulSoup(response,'lxml')
    data_list = {}

    # 获取姓名，英文名
    nameinfo = soup.find(class_='table').find('h1').get_text()
    name = nameinfo.split(' ')[0]
    E_name = nameinfo.split(' ', 1)[1]

    # 为避免缺失值，不能直接提取数据。利用列表转字符串的方式巧妙清洗
    gender = re.findall('.*?<li  ><strong>性别：</strong>(.*?)</li>.*?', response, re.S)
    gender = ''.join(gender)
    birth = re.findall('.*?<li  ><strong>出生日期：</strong>(.*?)</li>*?', response, re.S)
    birth = ''.join(birth)
    height = re.findall('.*?<li  ><strong>身高：</strong>(.*?)</li>.*?', response, re.S)
    height = ''.join(height)
    weight = re.findall('.*?<li  ><strong>体重：</strong>(.*?)</li>.*?', response, re.S)
    weight = ''.join(weight)
    event = re.findall('.*?<li  ><strong>项目：</strong>(.*?)</li>.*?', response, re.S)
    event = ''.join(event)
    nationplace = re.findall('.*?<li  ><strong>籍贯：</strong>(.*?)</li>.*?', response, re.S)
    nationplace = ''.join(nationplace)


    # 获取照片
    picture = soup.find(class_='logo').find('img')['src']

    # 获取个人简介
    introduce_pre = soup.find(class_='text').get_text()
    introduce = introduce_pre.replace('\n', '')

    # 数据整合，放入字典中
    data_list['name'] = name
    data_list['E_name'] = E_name
    data_list['gender'] = gender
    data_list['birth'] = birth
    data_list['height'] = height
    data_list['weight'] = weight
    data_list['event'] = event
    data_list['nationplace'] = nationplace
    data_list['picture'] = picture
    data_list['introduce'] = introduce
    data_list['href'] = url

    return data_list


# 写入表头
def write_csv_headers(headers):
    f = open('athletes_datas.csv','a',encoding='gb18030', newline='')
    f_csv = csv.DictWriter(f, headers)
    f_csv.writeheader()


# 写入数据
def write_csv_rows(headers ,data):
    # 写入行
    f = open('athletes_datas.csv','a',encoding='gb18030', newline='')
    f_csv = csv.DictWriter(f, headers)
    f_csv.writerow(data)
    f.close()


# 主函数
def main():
    # 表头
    headers = ['name', 'E_name', 'gender', 'birth', 'height', 'weight',
               'event', 'nationplace', 'picture', 'introduce', 'href']
    write_csv_headers(headers)

    url = 'http://info.2016.163.com/chinaathlete/list_item/'
    response = get_request(url)
    hrefs = get_athletes_url(response)
    hrefs = list(hrefs)
    for i in tqdm(range(355)):
        href = hrefs[i]
        data = get_detailinfo(href)
        write_csv_rows(headers , data)


if __name__ == '__main__':
    main()
