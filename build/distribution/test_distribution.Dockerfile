FROM ubuntu:20.04

RUN apt-get update --fix-missing && apt install -y --no-install-recommends software-properties-common
RUN add-apt-repository -y ppa:alex-p/tesseract-ocr5
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata
RUN apt-get install -y --no-install-recommends libgl1 libglib2.0-0 tesseract-ocr tesseract-ocr-pol poppler-utils
# RUN apt-get install -y --no-install-recommends git wget unzip

# -- Python --
RUN apt-get install -y python3.9 python3.9-dev python3.9-distutils curl build-essential protobuf-compiler
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3.9 get-pip.py
RUN python3.9 -m pip install --upgrade pip

