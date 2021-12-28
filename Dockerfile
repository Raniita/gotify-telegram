FROM python:slim

WORKDIR /app

RUN apt-get update

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "./main.py"]