FROM debian:latest
RUN <<EOF
apt update
apt install -y mosquitto
EOF

#RUN systemctl enable mosquitto.service

EXPOSE 1883
CMD ["tail", "-f", "/dev/null"]
 

