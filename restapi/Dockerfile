FROM python:3.8.3

ENV stage_app=production

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD ["bash","docker-entrypoint.sh","${stage_app}"]
