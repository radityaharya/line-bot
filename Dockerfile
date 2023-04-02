FROM python:3.9
ADD . /line-bot
WORKDIR /line-bot
RUN apt-get update && apt-get install -y python3-pip && apt-get install -y git
RUN pip install --upgrade pip
ENV TZ="Asia/Jakarta"
RUN pip install -r requirements.txt
RUN apt update 
RUN apt install tzdata -y
RUN pip install gunicorn
EXPOSE 80
RUN git init
RUN git submodule update --init --recursive
CMD ["gunicorn", "-b", "0.0.0.0:80", "app:run" "--timeout", "1000"]
