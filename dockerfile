FROM python:latest

WORKDIR /contratapro_python

COPY requirements.txt /contratapro_python/

RUN pip install --no-cache-dir -r requirements.txt uvicorn[standard]

COPY . /contratapro_python

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
