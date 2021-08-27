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
from city import city, getcsv

startDAYSPNG = "<!-- BEGIN UPDATINGDAYSPNG BOARD-->"
stopDAYSPNG = "<!-- END UPDATINGDAYSPNG BOARD-->"
tz = pytz.timezone('Europe/Berlin')
now = datetime.now(tz)
weekday = now.weekday()

def main(Stadt):
    for my_date in range(0,7):
        dayname = calendar.day_name[my_date]
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
        fig, ax = plt.subplots(1)
        if len(olddates) == 0:
            continue
        try:
            xnew = np.linspace(olddates.min(), olddates.max(), 300)
            gfg = make_interp_spline(olddates, OldData, k=3)
            SmoothedOldData = gfg(xnew)

            plt.plot_date(xnew, SmoothedOldData, '-', label="Average")
        except:
            plt.plot_date(olddates, OldData, '-', label="Average")
        plt.legend(loc="upper left")
        plt.xticks(rotation=40)
        plt.gcf().subplots_adjust(bottom=0.15)
        plt.xlabel('Time')
        plt.ylim((0, 100))
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
        plt.ylabel('occupancy[%]')
        plt.title(f'Occupancy {dayname}')
        Stadt.pngfile = f"./png/OtherDays/{Stadt.ShortForm}{dayname}.png"
        if os.path.exists(Stadt.pngfile):
            os.remove(Stadt.pngfile)
        fig.savefig(Stadt.pngfile)
        plt.close()



def replace_img_name_days(original_text, Stadte):
    delimiter_a = startDAYSPNG
    delimiter_b = stopDAYSPNG
    can_replace, leading_text, trailing_text = get_other_text(original_text, delimiter_a, delimiter_b)
    if not can_replace:
        return original_text

    replacing_text = '\n|'
    for Stadt in Stadte:
        replacing_text += f" {Stadt.BoulderName} |"
    replacing_text += '\n'
    replacing_text += '|'
    for i in range(len(Stadte)):
        replacing_text += ":-:|"
    replacing_text += '\n'
    for my_date in range(0, 7):
        dayname = calendar.day_name[my_date]
        for Stadt in Stadte:
            png_name = f"png/OtherDays/{Stadt.ShortForm}{dayname}.png"
            if os.path.exists(png_name):
                replacing_text += f'|<img src="{png_name}">'
            else:
                replacing_text += f'|<img src="./png/Working.png">'
        replacing_text += '|\n'

    return leading_text + delimiter_a + replacing_text + delimiter_b + trailing_text


def get_other_text(original_text, delimiter_a, delimiter_b):
    if original_text.find(delimiter_a) == -1 or original_text.find(delimiter_b) == -1:
        return False, '', ''

    leading_text = original_text.split(delimiter_a)[0]
    trailing_text = original_text.split(delimiter_b)[1]
    return True, leading_text, trailing_text


def write_to_readme(Stadt):
    with open('README.md', 'r', encoding='utf-8') as file:
        readme = file.read()
        readme = replace_img_name_days(readme,Stadt)

    with open('README.md', 'w', encoding='utf-8') as file:
        # Write new board & list of movements
        file.write(readme)

if __name__ == '__main__':
    cities = []
    for cit in getcsv():
        cithere = city(cit)
        cities.append(cithere)
        main(cithere)
    write_to_readme(cities)
    
