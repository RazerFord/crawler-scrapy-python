from os import environ
import subprocess
from time import sleep
import schedule

iteration = 1
time = str()
start = False

def run():
    global iteration
    with open("log", "a") as f:
        print("start crawl")
        f.write(f"start scrapy iteration {iteration}\n")
        out = subprocess.check_output(
            "cd ./netology/ && scrapy crawl programs --logfile log",
            shell=True,
            universal_newlines=True,
        )
        f.write(time)
        f.write(out)
        f.write("stop scrapy\n\n")
        iteration += 1
        print("sleep crawl")


def initSchedule():
    sleep(5)
    global time, start
    if "TIME_BREAK" in environ:
        schedule.every(int(environ["TIME_BREAK"])).seconds.do(run)
        time = f"time break: {environ['TIME_BREAK']}\n"
        start = True
    elif "EXACT_TIME" in environ:
        schedule.every().day.at(environ["EXACT_TIME"]).do(run)
        time = f"exact time: {environ['EXACT_TIME']}\n"
        start = True

if __name__ == "__main__":
    initSchedule()
    while start:
        schedule.run_pending()
        sleep(1)
