FROM ubuntu:latest
RUN apt update 
RUN apt upgrade -y


# installation of dependencies
RUN apt install -y xvfb
RUN apt install -y wget
RUN apt install -y gnupg
RUN apt install at -y


# installation of Firefox and the Geckodriver
RUN apt install firefox -y
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.29.0/geckodriver-v0.29.0-linux64.tar.gz
RUN tar -xvzf geckodriver*
RUN chmod +x geckodriver
RUN mv geckodriver /usr/local/bin/
RUN export PATH=$PATH:/usr/local/bin/geckodriver


# installation of Python
RUN apt install python3 -y
RUN apt install python3-pip -y


# installation of the scraper
RUN mkdir app
COPY requirements.txt main.py /app/
COPY scraper /app/scraper
COPY thirdPartyplugins /app/thirdPartyplugins
WORKDIR /app

# installation of pip packages
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# create log folder
RUN mkdir log

# configure and start Xvfb to emulate monitor
RUN export DISPLAY=:0
RUN Xvfb :0 -screen 0 1920x1080x24 &

# Definition of the call. the call of the schedule file is written into a file.
# This file is opened then, so that the container does not close again but
# for further commands remains open
# Source:
# https://phpfog.com/how-to-keep-docker-containers-running/
CMD /app/config/schedule.sh >> /app/log/schedule.log && tail -f /app/log/schedule.log
