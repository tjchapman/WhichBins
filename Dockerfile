FROM python:3.12-alpine
WORKDIR /main
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . . 

CMD [ "python", "./main.py"]