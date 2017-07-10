import os
from celery import Celery
from celery.utils.log import get_task_logger

app = Celery('stocks')
logger = get_task_logger(__name__)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    enable_utc=True,
    broker_url=os.environ['RABBITMQ_URL'],
    imports=['stock_scraper.services.index'])
