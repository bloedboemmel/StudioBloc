import calendar
import csv
import json
import sys

import pause
from datetime import datetime, timedelta, date, timezone
from time import sleep
import pytz
from bs4 import BeautifulSoup
import requests

header = ['Zeit', 'Besucher', 'Frei', 'Auslastung']
url = 'https://www.dersteinbock-nuernberg.de/'
tz = pytz.timezone('Europe/Berlin')


def getnow(Stadt):
    ans = requests.get(Stadt.BoulderadoUrl)
    soup = BeautifulSoup(ans.content, 'html.parser')
    aktuellbesetzt = soup.find_all(class_="actcounter-content")
    besetzt = int(aktuellbesetzt[0].text)
    aktuellfrei = soup.find_all(class_="freecounter-content")
    frei = int(aktuellfrei[0].text)

    belegung = [datetime.now(tz).replace(minute=((datetime.now(tz).minute // 5) * 5)).strftime("%d.%m.%Y, %H:%M:%S"),
                besetzt, frei, round((besetzt / (frei + besetzt)) * 100)]
    dumpit(belegung, Stadt)


def dumpit(data, Stadt):
    with open(f'today/{Stadt.ShortForm}Belegung.csv', 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f, delimiter=";")
        # write multiple rows
        writer.writerow(data)
    write_average(data[3], Stadt)


def write_average(Anteil, Stadt):
    my_date = date.today()
    dayname = calendar.day_name[my_date.weekday()]
    with open(f'days/{Stadt.ShortForm}/{dayname}.txt') as file:
        d = json.load(file)
    d[datetime.now(tz).replace(minute=((datetime.now(tz).minute // 15) * 15)).strftime("%H:%M")].append(Anteil)

    with open(f'days/{Stadt.ShortForm}/{dayname}.txt', 'w') as outfile:
        json.dump(d, outfile)

