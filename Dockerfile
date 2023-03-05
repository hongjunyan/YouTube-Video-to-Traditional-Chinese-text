FROM python:3.8.15

COPY ./ /audio2text
WORKDIR /audio2text

RUN pip install -r requirements.txt

CMD ["python3", "main.py"]