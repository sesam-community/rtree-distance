FROM ubuntu:16.04
MAINTAINER Baard H. Rehn Johansen "baard.johansen@sesam.io"

COPY ./service /service

RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN pip3 install -r /service/requirements.txt
RUN apt-get install -y python3-rtree

EXPOSE 5000/tcp
ENTRYPOINT ["python3"]
CMD ["./service/service.py"]

