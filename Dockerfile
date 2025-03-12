
FROM python:3.10


WORKDIR /project

COPY ./requirements_freeze.txt /project/requirements_freeze.txt

RUN pip install --no-cache-dir --upgrade -r /project/requirements_freeze.txt

COPY ./ /project

CMD ["fastapi", "run", "main.py", "--port", "80"]
