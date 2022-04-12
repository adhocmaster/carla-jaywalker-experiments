# syntax=docker/dockerfile:1
# FROM ubuntu:latest
FROM python:3.7.13
WORKDIR /app


# RUN ["echo", "I don't use a shell at all"]
# SHELL ["/bin/bash", "-c"]

# RUN pip --version 
RUN ["python", "--version"]
RUN ["pip", "--version"]
RUN echo "Installing Libraries"

# RUN pip install carla

COPY . .

RUN apt-get update && apt-get install -y apt-transport-https

RUN apt-get install -y libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsdl1.2-dev libsmpeg-dev subversion libportmidi-dev ffmpeg libswscale-dev libavformat-dev libavcodec-dev libfreetype6-dev
# pip install pygame==1.9.6
# RUN apt-get install python-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsdl1.2-dev libsmpeg-dev python-numpy subversion libportmidi-dev ffmpeg libswscale-dev libavformat-dev libavcodec-dev libfreetype6-dev
# RUN apt-get install -y python-dev
RUN pip install -r requirements.txt

RUN git clone https://github.com/adhocmaster/carla-jaywalker-experiments.git
