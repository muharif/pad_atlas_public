FROM python:3.11-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /code
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && useradd --create-home --uid 10001 atlas
COPY __init__.py app.py /code/pad_atlas_public/
COPY components/ /code/pad_atlas_public/components/
COPY pages/ /code/pad_atlas_public/pages/
COPY utils/ /code/pad_atlas_public/utils/
COPY assets/ /code/pad_atlas_public/assets/
COPY Parquet/ /code/pad_atlas_public/Parquet/
COPY wsgi.py /code/wsgi.py
COPY scripts/check_data.py /code/check_data.py
RUN python /code/check_data.py /code/pad_atlas_public/Parquet
USER atlas
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4", "--timeout", "120", "--access-logfile", "-", "wsgi:server"]
