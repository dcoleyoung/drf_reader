#scraper test of results
import requests
from bs4 import BeautifulSoup

headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
url = "https://entries.horseracingnation.com/entries-results/del-mar/2022-08-19"
req = requests.get(url, headers)
winners_dict = {}
soup = BeautifulSoup(req.content, 'html.parser')

runners = []
also_rans = soup.find_all("div", {"class": "mb-3 race-also-rans"})
for ar in also_rans:
    race_also_rans = ar.get_text().strip()
    r = race_also_rans.split("Also rans:")[1].split(',')
    runners += r


tables = soup.find_all("table",{"class":"table table-hrn table-payouts"})
for table in tables:
    tbody = table.find("tbody")
    first_row = tbody.find("tr")
    cells = first_row.findAll("td")
    name = cells[0].get_text().strip()
    post = cells[1].find("img")['title']
    price = cells[2].get_text().strip()
    winners_dict[name] = {'price': price, 'post':post}

    rows = tbody.find_all('tr')
    for row in rows:
        cells = row.findAll("td")
        name = cells[0].get_text().strip()
        runners.append(name)


entry_tables = soup.find_all("table",{"class":"table table-sm table-hrn table-entries"})
for table in entry_tables:
    rows = table.find_all('tr',{"class":"scratched"})
    for row in rows:
        cells = row.findAll("td")

        name = cells[3].find("h4")
        fname = name.get_text().strip()

print(runners)