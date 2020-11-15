FROM python:3.6
WORKDIR /app
ADD requirements.txt ./
RUN pip install -r requirements.txt
ADD *.py ./
ENV FLASK_APP=server
CMD flask run --host=0.0.0.0 --port=${PORT:-5000}
