FROM python:3.11.5

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /opt/app

# Install Poetry
RUN pip install poetry

# Copy only requirements to cache them in docker layer
COPY src ./src
COPY resources ./resources
COPY pyproject.toml poetry.lock ./


# Project initialization:
RUN poetry config virtualenvs.create false \
    && poetry install

WORKDIR ./src
#CMD ["python", "./excelParser.py"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]