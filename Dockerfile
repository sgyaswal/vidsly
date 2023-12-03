# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8-slim-buster

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# For MS SQL Setup in image
RUN apt-get update
RUN apt-get install -y build-essential libssl-dev libffi-dev python3-dev
RUN apt-get install -y unixodbc-dev
RUN apt-get install -y curl
RUN apt-get install -y apt-utils
RUN apt-get install -y libmariadb-dev
RUN apt-get install -y python3-tk
# Add SQL Server ODBC Driver 17 for Ubuntu 18.04
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y --allow-unauthenticated msodbcsql17
RUN ACCEPT_EULA=Y apt-get install -y --allow-unauthenticated mssql-tools
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc


# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt --use-deprecated=legacy-resolver

WORKDIR /app
COPY . /app
RUN mkdir -p /app/logs
RUN chmod 755 /app/logs
# COPY /backend/.env /app/backend
# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
# File wsgi.py was not found in subfolder: 'rest-api'. Please enter the Python path to wsgi file.
# RUN python manage.py migrate --no-input 
RUN python manage.py collectstatic --no-input

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "hr_review.wsgi"]
