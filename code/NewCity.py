import calendar
import json
import os
import sys
from datetime import datetime, timedelta

times = [[10, 23], [10, 23], [10, 23], [10, 23], [10, 23], [10, 23], [10, 23], [10, 23]]


def dummydays(Stadt):
    if not os.path.exists(f'days/{Stadt}'):
        os.mkdir(f'days/{Stadt}')
    for my_date in range(0, 7):
        day = calendar.day_name[my_date]
        print(day)

        n = {}
        time = datetime.strptime(f"{times[my_date][0]}:00", "%H:%M")
        while time < datetime.strptime(f"{times[my_date][1]}:00", "%H:%M"):
            new_time = time.replace(minute=((time.minute // 15) * 15)).strftime("%H:%M")
            if new_time not in n.keys() or len(n[new_time]) == 0:
                n[new_time] = []

            time += timedelta(minutes=15)
        with open(f'days/{Stadt}/{day}.txt', 'w') as outfile:
            json.dump(n, outfile)


if __name__ == '__main__':
    Stadt = sys.argv[1]
    dummydays(Stadt)
