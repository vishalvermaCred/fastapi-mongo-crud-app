FROM python:3.9-slim
RUN apt-get -yq update && \
    apt-get install -y build-essential

RUN mkdir -p /code
RUN mkdir -p /var/log/logs/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create app directory
WORKDIR /code
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
RUN pip3 install --upgrade pip

# Bundle app source
COPY ./ /code

RUN chmod 755 -R /code
RUN chmod 777 -R /code/
RUN chmod 777 -R /var/log/logs/

EXPOSE 9200

CMD uvicorn app.server:app --host 0.0.0.0 --port 9200 --no-access-log
