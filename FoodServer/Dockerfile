FROM python:3.11-alpine3.17
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /FoodServer
# RUN apk update

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

RUN python manage.py makemigrations
RUN python manage.py migrate

CMD [ "python", "manage.py", "runserver" ]