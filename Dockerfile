FROM python:3.11-alpine3.17
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /FoodServer

COPY . .
RUN pip install --no-cache-dir -r ./FoodServer/requirements.txt

EXPOSE 8000

RUN rm -r ./db.sqlite3
RUN python manage.py makemigrations
RUN python manage.py migrate
RUN python manage.py createsuperuser --username=admin --email=admin@foodserver.com --noinput
# Change the default admin password once the system is running

# CMD [ "python", "manage.py", "runserver" ]
CMD ["gunicorn", "--bind=0.0.0.0:8000", "--workers=2", "FoodServer.wsgi"]