#Container image that runs your code
FROM --platform=linux/amd64 python:3.10-slim

#Set the working directory
WORKDIR /application_IOA

#Copies your code file from your action repository to the filesystem path `/` of the container
COPY . /application_IOA

#RUN is triggered on docker build in yml file
RUN pip install -r /application_IOA/requirements.txt

#RUN python3 Main.py
#CMD ["ls", "/application_IOA"]
CMD ["python", "/application_IOA/_main.py"]