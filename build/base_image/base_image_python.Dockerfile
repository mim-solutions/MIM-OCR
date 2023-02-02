FROM ghcr.io/mim-solutions/mim-ocr_base_ubuntu
ARG python_version

RUN echo $python_version:

# -- Python --
RUN apt-get install -y python${python_version} python${python_version}-dev python${python_version}-distutils curl build-essential protobuf-compiler
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python${python_version} get-pip.py
RUN python${python_version} -m pip install --upgrade pip

# ----- ROBERTA NER FEATURES ------
RUN pip install gdown

RUN mkdir dependencies
WORKDIR dependencies

# clone the repository
RUN if [ "$python_version" = "3.9" ] ; then git clone https://github.com/mczuk/xlm-roberta-ner ; fi

# download the Polish RoBERTa base model
RUN if [ "$python_version" = "3.9" ] ; then mkdir xlm-roberta-ner/models/roberta_base_fairseq -p ; fi
RUN if [ "$python_version" = "3.9" ] ;  \
        then wget https://github.com/sdadas/polish-roberta/releases/download/models/roberta_base_fairseq.zip &&\
        unzip roberta_base_fairseq.zip -d xlm-roberta-ner/models/roberta_base_fairseq &&\
        rm roberta_base_fairseq.zip ; \
    fi

#download the pre-trained model
RUN if [ "$python_version" = "3.9" ] ;  \
      then gdown 1e0psQazmePJOKUv3VupV4q7KcyZ1_dFM &&\
      unzip ner_pretrained_model.zip -d xlm-roberta-ner/models &&\
      rm ner_pretrained_model.zip ; \
    fi

#downgrade pip to 22.3.1 for python 3.10 due to https://github.com/pypa/pip/issues/11770
RUN if [ "$python_version" = "3.10" ] ;  \
      then  python3.10 -m pip install pip==22.3.1 ; \
    fi

# ----- ---------------------------
WORKDIR  /

COPY ./build/base_image/base_requirements.txt ./base_requirements.txt

RUN python${python_version} -m pip install -r base_requirements.txt