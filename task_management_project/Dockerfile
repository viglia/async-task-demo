FROM python:3.7

WORKDIR /usr/src/app

COPY  requirements.txt manage.py pytest.ini ./

COPY task_app task_app/

COPY task_management_project task_management_project/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

run python manage.py makemigrations \
    && python manage.py migrate

EXPOSE 8000

ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8000"] 




