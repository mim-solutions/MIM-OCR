FROM ubuntu:20.04

RUN apt-get update --fix-missing && apt install -y --no-install-recommends software-properties-common
RUN add-apt-repository -y ppa:alex-p/tesseract-ocr5
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata
RUN apt-get install -y --no-install-recommends libgl1 libglib2.0-0 tesseract-ocr tesseract-ocr-pol poppler-utils

# -- Python --
RUN apt-get install -y python3.9 python3.9-dev python3.9-distutils curl build-essential protobuf-compiler
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3.9 get-pip.py
RUN python3.9 -m pip install --upgrade pip

RUN python3.9 -m pip install mim_ocr
RUN python3.9 -m pip install pytest
COPY ./tests /mim/tests
COPY ./config /mim/config
WORKDIR /mim
RUN mkdir local
RUN mkdir local/keyword_features_hyperscan_databases
ENV MIM_OCR_CONFIG_PATH=/mim/config/test_mim_ocr_conf.yaml
RUN python3.9 -m pytest tests

