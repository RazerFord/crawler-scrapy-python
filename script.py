from os import environ
import subprocess
from time import sleep


def run():
    iteration = 1
    while True:
        with open("log", "a") as f:
            print("start")
            f.write(f"start scrapy iteration {iteration}\n")
            out = subprocess.check_output(
                "cd ./netology/ && scrapy crawl programs --logfile log",
                shell=True,
                universal_newlines=True,
            )
            f.write(f"time break: {environ['TIME_BREAK']}\n")
            f.write(out)
            f.write("stop scrapy\n\n")
            iteration += 1
            print("sleep")
            sleep(10)
            # sleep(int(environ["TIME_BREAK"]))


if __name__ == "__main__":
    run()
