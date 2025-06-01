FROM ubuntu:latest
RUN apt-get update
#RUN apt install tar
#RUN wget https://mosquitto.org/files/source/mosquitto-2.0.21.tar.gz

#RUN tar -xzvf mosquitto-2.0.21.tar.gz
#RUN cd mosqtuitto-2.0.21

RUN apt install -y mosquitto
RUN apt install -y mosquitto-clients
RUN apt install -y sqlite3
