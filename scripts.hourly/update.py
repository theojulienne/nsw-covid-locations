#!/usr/bin/env python3

import requests
import bs4
from datetime import datetime

t = open('case-locations.md', 'w')

url = 'https://www.health.nsw.gov.au/Infectious/covid-19/Pages/case-locations-and-alerts.aspx'
soup = bs4.BeautifulSoup(requests.get(url, verify=True).text, 'html.parser')

caseHeaderTable = soup.select('#tbl-case-locations thead tr th')
header = list(map(lambda x: x.text, caseHeaderTable))

headerSizes = [
    ('Last updated', 15),
    ('Type', 20),
    ('Suburb', 15),
    ('Venue', 25),
    ('Date and time of exposure', 60),
]

fmt = '| {} |\n'.format(' | '.join(map(lambda x: '{:' + str(x[1]) + '}', headerSizes)))
t.write(fmt.format(*map(lambda x: x[0], headerSizes)))

t.write('| {} |\n'.format(' | '.join(['---'] * len(headerSizes))))

def mapType(t):
    if 'Get tested immediately. Self-isolate until you get a negative result.' in t:
        return 'Casual Contact'
    elif 'Get tested immediately and self-isolate for 14 days' in t:
        return 'Close Contact'
    elif 'Monitor for symptoms' in t:
        return 'Monitor for symptoms'
    elif 'Get tested immediately. People with no symptoms do not need to isolate while waiting for their test result.' in t:
        return 'Test (isolate w/ symptoms)'
    assert False, t

caseLocationTable = soup.select('#tbl-case-locations tbody tr')
rows = []
for row in caseLocationTable:
    cells = list(map(lambda x: x.text, row.find_all('td')))
    rowHash = dict(zip(header, cells))

    rowHash['Type'] = mapType(rowHash['Type'])
    rows.append(rowHash)

# parse date in format DD/MM/YYYY to a datetime object
def parseDate(date):
    return datetime.strptime(date, '%d/%m/%Y')

rows.sort(key=lambda x: (parseDate(x['Last updated']), x['Type'], x['Suburb']))
rows.reverse()

for rowHash in rows:
    t.write(fmt.format(*map(lambda x: rowHash[x[0]].replace('\n', ''), headerSizes)))