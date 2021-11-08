FROM python:3.8

EXPOSE 8080

# Allow statements and log messages to immediately appear in the Cloud Run logs
ENV PYTHONUNBUFFERED True

RUN pip install --upgrade pip
# Set the working directory to /files
WORKDIR /sample2pub

COPY ./files/requirements.txt /sample2pub/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

COPY . .

ENV GOOGLE_APPLICATION_CREDENTIALS=/sample2pub/files/GCP_sa_file.json

# 當 Docker 容器啟動時，自動執行 app.py
CMD ["python", "/sample2pub/files/main_app.py"]
