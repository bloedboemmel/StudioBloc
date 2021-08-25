import calendar
import csv
import json
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
    if Stadt == 'Darmstadt':
        ans = requests.get(src="https://www.boulderado.de/boulderadoweb/gym-clientcounter/index.php?mode=get&token"
                               "=eyJhbGciOiJIUzI1NiIsICJ0eXAiOiJKV1QifQ.eyJjdXN0b21lciI6IlN0dWRpb0Jsb2MifQ"
                               ".fPOKp49FQ9geu6CC9ueB3U3yW2VmwKxD5M0BIobtWQc")
    elif Stadt == 'Mannheim':
        ans = requests.get(
            "https://www.boulderado.de/boulderadoweb/gym-clientcounter/index.php?mode=get&token"
            "=eyJhbGciOiJIUzI1NiIsICJ0eXAiOiJKV1QifQ.eyJjdXN0b21lciI6IlN0dWRpb2Jsb2NNYW5uaGVpbTM5MjAxOSJ9"
            ".DVfdyyiQeryvL47EL1oEIIhaUMKpPxeeEsAOLMGVAlU")

    else:
        return

    soup = BeautifulSoup(ans.content, 'html.parser')
    aktuellbesetzt = soup.find_all(class_="actcounter-content")
    besetzt = int(aktuellbesetzt[0].text)
    aktuellfrei = soup.find_all(class_="freecounter-content")
    frei = int(aktuellfrei[0].text)

    belegung = [datetime.now(tz).replace(minute=((datetime.now(tz).minute // 5) * 5)).strftime("%d.%m.%Y, %H:%M:%S"),
                besetzt, frei, round((besetzt / (frei + besetzt)) * 100)]
    dumpit(belegung, Stadt)


def dumpit(data, Stadt):
    with open(f'./today/{Stadt}Belegung.csv', 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f, delimiter=";")
        # write multiple rows
        writer.writerow(data)
    write_average(data[3], Stadt)


def write_average(Anteil, Stadt):
    my_date = date.today()
    dayname = calendar.day_name[my_date.weekday()]
    with open(f'days/{Stadt}/{dayname}.txt') as file:
        d = json.load(file)

    d[datetime.now(tz).replace(minute=((datetime.now(tz).minute // 15) * 15)).strftime("%H:%M")].append(Anteil)

    with open(f'days/{Stadt}/{dayname}.txt', 'w') as outfile:
        json.dump(d, outfile)


if __name__ == '__main__':
    while True:
        if 9 <= datetime.now(tz).hour < 22:
            try:
                getnow('Nürnberg')
                sleep(60)
            except:
                header = header
                sleep(60)
        else:
            n = datetime.now(tz)
            n += timedelta(days=1)
            n.replace(hour=9, minute=0, second=0, microsecond=0)
            pause.until(n)
