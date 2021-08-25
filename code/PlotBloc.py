import calendar
import glob
import json
import os
import sys
from datetime import datetime, timedelta, date
import pytz
import numpy as np
from scipy.interpolate import make_interp_spline
import GetNewData
import matplotlib
import matplotlib.pyplot as plt

start = "<!-- BEGIN UPDATINGDATA BOARD {Stadt}-->"
stop = "<!-- END UPDATINGDATA BOARD {Stadt}-->"

startPNG = "<!-- BEGIN UPDATINGPNG BOARD {Stadt}-->"
stopPNG = "<!-- END UPDATINGPNG BOARD {Stadt}-->"
tz = pytz.timezone('Europe/Berlin')
now = datetime.now(tz)
weekday = now.weekday()
times = [[10, 23], [10, 23], [10, 23], [10, 23], [10, 23], [9, 22], [9, 22], [9, 22]]


def main(Stadt):
    GetNewData.getnow(Stadt)
    import csv

    with open(f'./today/{Stadt}Belegung.csv', newline='') as csvfile:

        spamreader = csv.reader(csvfile, delimiter=';')
        belegung = []
        zeit = []
        for row in spamreader:
            belegung.append(int(row[3]))
            besucher = int(row[1])
            frei = int(row[2])
            zeit.append(datetime.strptime(row[0], "%d.%m.%Y, %H:%M:%S"))

    my_date = date.today()
    dayname = calendar.day_name[my_date.weekday()]
    with open(f'days/{Stadt}/{dayname}.txt') as file:
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
            OldAverage = gfg(dates[-1])
        except:
            plt.plot_date(olddates, OldData, '-', label="Average")
            OldAverage = OldData[-1]
        plt.legend(loc="upper left")
        plt.plot_date(dates[-1], belegung[-1], 'r*')
        plt.xticks(rotation=40)
        plt.gcf().subplots_adjust(bottom=0.15)
        plt.xlabel('Time')
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
        plt.ylabel('occupancy[%]')
        plt.title(f'Occupancy {dayname}')
        pngfile = f"./png/{Stadt}{now.strftime('%H_%M_%S')}.png"
        for filename in glob.glob(f"./png/{Stadt}*"):
            os.remove(filename)
        fig.savefig(pngfile)
        write_to_readme(besucher, frei, belegung[-1], OldAverage, pngfile, Stadt)
    except:
        pngfile = "./png/Working.png"
        write_to_readme(besucher, frei, belegung[-1], 0, pngfile, Stadt)





def odd(number):
    if number % 2 == 0:
        return number - 1
    return number


def replace_text_between(original_text, visitors, free, percent, average, Stadt):
    delimiter_a = start.format(Stadt=Stadt)
    delimiter_b = stop.format(Stadt=Stadt)
    can_replace, leading_text, trailing_text = get_other_text(original_text, delimiter_a, delimiter_b)
    if not can_replace:
        return original_text
    percent = int(percent)
    average = int(average)
    if percent < average:
        replacement_text = f"{visitors} out of {visitors + free} allowed visitors. " \
                           f"--> {percent}% occupied! {int(average - percent)}% less than average!"
    elif percent == average:
        replacement_text = f"{visitors} out of {visitors + free} allowed visitors. " \
                           f"--> {percent}% occupied! That's average!"
    else:
        replacement_text = f"{visitors} out of {visitors + free} allowed visitors. " \
                           f"--> {percent}% occupied! {int(percent - average)}% more than average!"

    return leading_text + delimiter_a + replacement_text + delimiter_b + trailing_text


def replace_img_name(original_text, png_name, Stadt):
    delimiter_a = startPNG.format(Stadt=Stadt)
    delimiter_b = stopPNG.format(Stadt=Stadt)
    can_replace, leading_text, trailing_text = get_other_text(original_text, delimiter_a, delimiter_b)
    if not can_replace:
        return original_text
    return leading_text + delimiter_a + f'<img src="{png_name}">' + delimiter_b + trailing_text


def get_other_text(original_text, delimiter_a, delimiter_b):
    if original_text.find(delimiter_a) == -1 or original_text.find(delimiter_b) == -1:
        return False, '', ''

    leading_text = original_text.split(delimiter_a)[0]
    trailing_text = original_text.split(delimiter_b)[1]
    return True, leading_text, trailing_text


def write_to_readme(visitors, free, percent, average, png_name, Stadt):
    with open('README.md', 'r', encoding='utf-8') as file:
        readme = file.read()
        readme = replace_text_between(readme, visitors, free, percent, average, Stadt)
        readme = replace_img_name(readme, png_name, Stadt)

    with open('README.md', 'w', encoding='utf-8') as file:
        # Write new board & list of movements
        file.write(readme)




if __name__ == '__main__':
    if times[weekday][0] <= now.hour <= times[weekday][1]:
        main('Mannheim')
        main('Darmstadt')
    else:
        print("Not opened right now!")
        sys.exit(1)
