#!/usr/bin/env python3

import requests
import bs4
from datetime import datetime

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
mdHeader = []
mdHeader.append(fmt.format(*map(lambda x: x[0], headerSizes)))

mdHeader.append('| {} |\n'.format(' | '.join(['---'] * len(headerSizes))))

def mapType(t):
    if 'Get tested immediately. Self-isolate until you get a negative result.' in t:
        return 'Casual Contact'
    elif 'Get tested immediately and self-isolate for 14 days' in t or 'Get tested immediately and self-isolate until you receive further advice.' in t:
        return 'Close Contact'
    elif 'Monitor for symptoms' in t:
        return 'Monitor for symptoms'
    elif 'Get tested immediately. People with no symptoms do not need to isolate while waiting for their test result.' in t:
        return 'Test (isolate w/ symptoms)'
    else:
        return 'UNKNOWN'

caseLocationTable = soup.select('#tbl-case-locations tbody tr')
rows = []
for row in caseLocationTable:
    cells = list(map(lambda x: x.text, row.find_all('td')))
    rowHash = dict(zip(header, cells))
    if 'Type' not in rowHash or rowHash['Type'] == '':
        print(rowHash)
        continue
    rowHash['Type'] = mapType(rowHash['Type'])
    rows.append(rowHash)

# parse date in format DD/MM/YYYY to a datetime object
def parseDate(date):
    return datetime.strptime(date, '%d/%m/%Y')

def dump(filename, rows, key, reverse=False):
    rows = rows[:]
    with open(filename, 'w') as t:
        for h in mdHeader:
            t.write(h)
        rows.sort(key=key)
        if reverse:
            rows.reverse()
        for rowHash in rows:
            t.write(fmt.format(*map(lambda x: rowHash[x[0]].replace('\n', ''), headerSizes)))

dump('case-locations-by-updated.md', rows, key=lambda x: (parseDate(x['Last updated']), x['Suburb'], x['Venue']), reverse=True)
dump('case-locations-by-suburb.md', rows, key=lambda x: (x['Suburb'], x['Venue'], parseDate(x['Last updated'])))