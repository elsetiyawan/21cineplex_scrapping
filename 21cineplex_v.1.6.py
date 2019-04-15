#!/usr/bin/env python
# coding: utf-8

import requests
import re
import os

from bs4 import BeautifulSoup
from datetime import datetime

print("Preparing .....")
hariini = datetime.today().strftime('%Y%m%d')
loc = os.getcwd()
if os.path.isdir(loc+"/"+hariini) == False:
    os.makedirs(hariini)

print("Accessing m.21cineplex.com ..... ")
url_tujuan = "https://m.21cineplex.com/gui.list_city.php?sid="
url = requests.get(url_tujuan)
content = url.content
rapi = BeautifulSoup(content,"html.parser")


# ambil data kota dan kode
print("Grab city and movie data .....")
cities = []
cari = rapi.find_all("li", {"class": "list-group-item"})
for x in cari:
    elem = x.find("div")
    city_name = elem.text
    link = elem['onclick']
    city_id = re.search("city_id=(.*)'",link)
    city = {
        'city_id' : city_id.group(1),
        'city_name' : city_name
    }
    cities.append(city)

# get all data move and movie
all_data = []
for city in cities:
    cookies = dict(city_id=city['city_id'], city_name=city['city_name'])
    url = requests.get('https://m.21cineplex.com/index.php?sid=', cookies=cookies)
    content = url.content
    beauty = BeautifulSoup(content,"html.parser")
    daftar = beauty.find_all("div", {"class": "grid_movie"})
    for x in daftar:
        judul = x.find("div", {"class":"title"})
        link = x.find("a")['href']
        mov_id = re.search("movie_id=(.*)", link)
        data = {
            'city_id' : city['city_id'],
            'city_name' : city['city_name'],
            'movie_id' : mov_id.group(1),
            'movie_title' : judul.text
        }
        all_data.append(data)
cities = []

# write data
for x in all_data:
    judul = x['movie_title'].replace(":","").replace("?","").replace("/","")
    f = open(loc+"/"+hariini+"/"+judul+".txt",'a+')
    cookies = dict(city_id=x['city_id'], city_name=x['city_name'])
    url = requests.get("https://m.21cineplex.com/gui.schedule.php?sid=&find_by=2&movie_id="+x['movie_id']+"", cookies=cookies)
    content = url.content
    beauty = BeautifulSoup(content,"html.parser")
    jadwal = beauty.find_all("li", {"class":"list-group-item"})
    for x in jadwal:
        lokasi = x.find('a')
        tanggal = x.find("div", {"class":"col-xs-7"})
        tiket = x.find("span", {"class":"p_price"})
        jadwal = x.find("p", {"class":"p_time"})
        jam = jadwal.find_all("a", {"class":"btn"})
        f.write(lokasi.text.strip()+"\n")
        f.write(tanggal.text.strip()+tiket.text.strip()+"\n")
        jumlah_jam = len(jam)
        print(lokasi.text)
        print(tanggal.text+tiket.text)
        count = 1
        for x in jam:
            if count == jumlah_jam:
                f.write(x.text.strip())
            else:
                f.write(x.text.strip()+" ")
            print(x.text)
            count += 1
        f.write("\n")
    f.close()

