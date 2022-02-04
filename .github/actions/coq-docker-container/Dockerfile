FROM coqorg/coq:latest

RUN sudo apt-get update
RUN sudo apt-get install -y python3-pip

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]