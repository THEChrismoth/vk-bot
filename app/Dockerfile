FROM python:3.12.6
WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]