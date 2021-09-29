import requests
import csv
import html
from bs4 import BeautifulSoup

pagesAmount = 5  # Количество страниц, которые мы парсим
urlsOfEndPoints = []

headersList = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0'}

for i in range(pagesAmount):
    listOfSites = requests.get(f'http://moskva.regtorg.ru/comps/medicinskoe-oborudovanie/page{i + 1}.htm',
                               headers=headersList).text
    urlsSoup = BeautifulSoup(listOfSites, 'lxml')

    block = urlsSoup.find_all("div", class_='item', attrs={'itemtype': 'http://schema.org/Organization'})
    items = [e.div.a.attrs['href'] for e in block]

    urlsOfEndPoints.extend(items)

result = [['Organization name', 'Phone', 'Url', 'INN']]

for index, item in enumerate(urlsOfEndPoints):
    orgPageText = requests.get(item, headers=headersList).text
    orgSoup = BeautifulSoup(orgPageText, 'lxml')

    name = html.unescape(orgSoup.find("h2", text=lambda t: t and 'Полное название организации' in t).text.split(':')[1].strip())
    phone = orgSoup.find("span", class_='lbl3', text=lambda t: t and 'Телефон' in t)
    phone = phone.find_next("span").text if phone is not None else '-'

    url = orgSoup.find("span", class_='lbl3', text=lambda t: t and 'Официальный сайт' in t)
    url = url.find_next("a").attrs['href'] if url is not None else '-'

    contacts = orgSoup.find("span", class_='lbl3', text=lambda t: t and 'ИНН' in t)

    if contacts is not None:
        INN = contacts.next_element.next_element.replace(' ', '')
    else:
        INN = '-'

    result.append([name, phone, url, INN])

resFile = open('result.csv', 'w', newline='')
with resFile:
    writer = csv.writer(resFile)
    writer.writerows(result)
