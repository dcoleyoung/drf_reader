import requests
from bs4 import BeautifulSoup

headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
url = "https://entries.horseracingnation.com/entries-results/santa-anita/2021-02-20"
req = requests.get(url, headers)
winners_dict = {}
soup = BeautifulSoup(req.content, 'html.parser')
tables = soup.find_all("table",{"class":"table table-hrn table-payouts"})
for table in tables:
    tbody = table.find("tbody")
    first_row = tbody.find("tr")
    cells = first_row.findAll("td")
    name = cells[0].get_text().strip()
    post = cells[1].find("img")['title']
    price = cells[2].get_text().strip()
    winners_dict[name] = {'price': price, 'post':post}
print(winners_dict)
