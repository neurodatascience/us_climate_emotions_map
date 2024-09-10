FROM python:3.11-slim-buster

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./climate_emotions_map /app/climate_emotions_map
COPY ./code/assets /app/code/assets
COPY ./data /app/data

CMD ["gunicorn", "-b", "0.0.0.0:8050", "climate_emotions_map.app:server"]
