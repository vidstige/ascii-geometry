FROM python:3.6
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    mesa-utils libegl1-mesa xauth xvfb 

# Install python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /app

ENV DISPLAY=:99.0

COPY shaders/*.vert shaders/*.frag shaders/
COPY static/* ./static/
COPY *.py ./

CMD xvfb-run waitress-serve --port=${PORT:-5000} server:app
