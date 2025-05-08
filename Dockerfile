FROM python:3.9-slim
WORKDIR /app
COPY data_generator.py producer.py consumer.py requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["python","producer.py"]