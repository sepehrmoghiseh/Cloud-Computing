FROM python:3.11.0a6-alpine3.15

LABEL maintainer="Sepehr Moghiseh  <Sepehrmoghiseh@aut.ac.ir>"

WORKDIR .

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "main.py" ]