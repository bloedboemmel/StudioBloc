import calendar
import glob
import json
import os
import sys
from datetime import datetime, timedelta, date
import pytz
import numpy as np
from scipy.interpolate import make_interp_spline
import GetData
import matplotlib
import matplotlib.pyplot as plt
import csv
from city import city, getcsv

start = "<!-- BEGIN UPDATINGDATA BOARD-->"
stop = "<!-- END UPDATINGDATA BOARD-->"

startSUMMARY = "<!-- BEGIN UPDATINGSUMMARY BOARD-->"
stopSUMMARY = "<!-- END UPDATINGSUMMARY BOARD-->"

tz = pytz.timezone('Europe/Berlin')
now = datetime.now(tz)
weekday = now.weekday()


def main(Stadt):
    GetData.getnow(Stadt)

    with open(f'./today/{Stadt.ShortForm}Belegung.csv', newline='') as csvfile:

        spamreader = csv.reader(csvfile, delimiter=';')
        belegung = []
        zeit = []
        for row in spamreader:
            belegung.append(int(row[3]))
            Stadt.besucher = int(row[1])
            Stadt.frei = int(row[2])
            zeit.append(datetime.strptime(row[0], "%d.%m.%Y, %H:%M:%S"))

    my_date = date.today()
    dayname = calendar.day_name[my_date.weekday()]
    with open(f'days/{Stadt.ShortForm}/{dayname}.txt') as file:
        d = json.load(file)

    OldData = []
    OldTime = []
    now = datetime.now(tz)
    for key in d.keys():
        if len(d[key]) != 0:
            OldTime.append(datetime.strptime(key, "%H:%M").replace(year=now.year, month=now.month, day=now.day))
            OldData.append(sum(d[key]) / len(d[key]))

    olddates = matplotlib.dates.date2num(OldTime)
    dates = matplotlib.dates.date2num(zeit)
    fig, ax = plt.subplots(1)
    plt.plot_date(dates, belegung, '-', label="Now")
    xnew = np.linspace(olddates.min(), olddates.max(), 300)
    try:
        try:
            gfg = make_interp_spline(olddates, OldData, k=3)

            SmoothedOldData = gfg(xnew)
            plt.plot_date(xnew, SmoothedOldData, '-', label="Average")
            Stadt.OldAverage = gfg(dates[-1])
        except:
            plt.plot_date(olddates, OldData, '-', label="Average")
            Stadt.OldAverage = OldData[-1]
        plt.legend(loc="upper left")
        plt.plot_date(dates[-1], belegung[-1], 'r*')
        plt.xticks(rotation=40)
        plt.gcf().subplots_adjust(bottom=0.15)
        plt.xlabel('Time')
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
        plt.ylabel('occupancy[%]')
        plt.title(f'Occupancy {dayname}')
        Stadt.pngfile = f'./png/{Stadt.ShortForm}{now.strftime("%H_%M_%S")}.png'
        for filename in glob.glob(f'./png/{Stadt.ShortForm}*'):
            os.remove(filename)
            os.system(f'git rm --cached {filename}')
        fig.savefig(Stadt.pngfile)
        Stadt.belegung = belegung[-1]
        plt.close()
    except:
        Stadt.pngfile = "./png/Working.png"
        Stadt.OldAverage = 0
        Stadt.belegung = belegung[-1]


def odd(number):
    if number % 2 == 0:
        return number - 1
    return number


def replace_text_between(original_text, cities):
    delimiter_a = start
    delimiter_b = stop
    can_replace, leading_text, trailing_text = get_other_text(original_text, delimiter_a, delimiter_b)
    if not can_replace:
        return original_text

    for city in cities:
        get_text_for_average(city)
    replacement_text = "\n|"
    for city in cities:
        replacement_text += f" [{city.BoulderName}]({city.WebsiteUrl}) |"
    replacement_text += "\n"
    replacement_text += "|"
    for i in range(len(cities)):
        replacement_text += ":-:|"
    replacement_text += "\n"
    replacement_text += "|"
    for city in cities:
        replacement_text += " " + city.AverageText + " |"
    replacement_text += "\n"
    replacement_text += "|"
    for city in cities:
        replacement_text += f'<img src="{city.pngfile}">' + '|'
    replacement_text += "\n"
    return leading_text + delimiter_a + replacement_text + delimiter_b + trailing_text


def replace_summary(original_text, cities):
    delimiter_a = startSUMMARY
    delimiter_b = stopSUMMARY
    can_replace, leading_text, trailing_text = get_other_text(original_text, delimiter_a, delimiter_b)
    if not can_replace:
        return original_text

    string = "[{Stadt}]({Url})"
    replacement_text = "\n"
    replacement_text += "this is a plot of the official Visitor-Numbers of "
    if len(cities) == 1:
        replacement_text += string.format(Stadt=cities[0].BoulderName, Url=cities[0].WebsiteUrl)
    else:
        for city in cities[:-2]:
            replacement_text += string.format(Stadt=city.BoulderName, Url=city.WebsiteUrl) + ", "
        replacement_text += string.format(Stadt=cities[-2].BoulderName, Url=cities[-2].WebsiteUrl) + " and "
        replacement_text += string.format(Stadt=cities[-1].BoulderName, Url=cities[-1].WebsiteUrl)

    replacement_text += "\n"
    return leading_text + delimiter_a + replacement_text + delimiter_b + trailing_text


def get_text_for_average(Stadt):
    average = int(Stadt.OldAverage)
    visitors = Stadt.besucher
    free = Stadt.frei
    percent = int((visitors / (free + visitors)) * 100)
    if percent < average:
        text = f"{visitors} out of {visitors + free} allowed visitors. " \
               f"--> {percent}% occupied! {int(average - percent)}% less than average!"
    elif percent == average:
        text = f"{visitors} out of {visitors + free} allowed visitors. " \
               f"--> {percent}% occupied! That's average!"
    else:
        text = f"{visitors} out of {visitors + free} allowed visitors. " \
               f"--> {percent}% occupied! {int(percent - average)}% more than average!"
    Stadt.AverageText = text


def get_other_text(original_text, delimiter_a, delimiter_b):
    if original_text.find(delimiter_a) == -1 or original_text.find(delimiter_b) == -1:
        return False, '', ''

    leading_text = original_text.split(delimiter_a)[0]
    trailing_text = original_text.split(delimiter_b)[1]
    return True, leading_text, trailing_text


def write_to_readme(cities):
    with open('README.md', 'r', encoding='utf-8') as file:
        readme = file.read()
        readme = replace_text_between(readme, cities)
        readme = replace_summary(readme, cities)

    with open('README.md', 'w', encoding='utf-8') as file:
        # Write new board & list of movements
        file.write(readme)


if __name__ == '__main__':
    cities = []
    for cit in getcsv():
        cithere = city(cit)
        cities.append(cithere)
        if cithere.Times[weekday][0] <= now.hour <= cithere.Times[weekday][1]:
            main(cithere)
        else:
            print(f"{cithere.BoulderName} not opened right now!")
    if len(cities) > 0:
        write_to_readme(cities)
