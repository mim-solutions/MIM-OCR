FROM ubuntu:20.04
ARG python_version

RUN echo $python_version:

RUN apt-get update && apt install -y --no-install-recommends software-properties-common
RUN add-apt-repository -y ppa:alex-p/tesseract-ocr5
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata
RUN apt-get install -y --no-install-recommends libgl1 libglib2.0-0 tesseract-ocr tesseract-ocr-pol poppler-utils
RUN apt-get install -y --no-install-recommends git wget unzip
