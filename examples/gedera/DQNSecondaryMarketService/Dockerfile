# pull official base image
FROM python:3.11.9-slim

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# install dependencies
COPY requirements.txt /usr/src/app
RUN pip3 install -r requirements.txt

# copy project
COPY ./adabyron_environment /usr/src/app/adabyron_environment
COPY run.sh /usr/src/app/
COPY ./dqn_utils /usr/src/app/dqn_utils
COPY ./models /usr/src/app/models
COPY ./test_data /usr/src/app/test_data
COPY main_predict.py /usr/src/app/
EXPOSE 8001


RUN chmod +x ./run.sh
# CMD ["./run.sh"]
CMD ["python3", "main_predict.py"]