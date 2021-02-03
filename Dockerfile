# The first instruction is what image we want to base our container on
# We Use an official Python runtime as a parent image
FROM python:3.8.5

# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update && apt-get upgrade -y && apt-get install -y binutils libproj-dev gdal-bin

# create root directory for our project in the container
RUN mkdir /prophy

# Set the working directory to /mybrains
WORKDIR /prophy

# Copy the current directory contents into the container at /mybrains
ADD . /prophy/

# Install any needed packages specified in requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt


