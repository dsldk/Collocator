# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim

#RUN apt-get update && apt-get install -y git

# Copy local code to the container image.
ENV APP_HOME /code
WORKDIR $APP_HOME
COPY ./requirements.txt ./
COPY ./setup.py ./

# Install dependencies.
RUN pip install -r requirements.txt
RUN pip install -e .

# Copy the code from the host and run the application.
COPY ./collocator ./collocator

# Run the web service on container startup. Here we use the uvicorn
# webserver, with the FastAPI app.
WORKDIR $APP_HOME/collocator
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]