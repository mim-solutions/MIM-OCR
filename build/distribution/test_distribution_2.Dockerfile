FROM mim_ocr_base

RUN python3.9 -m pip install --extra-index-url https://test.pypi.org/simple/ mim_ocr
RUN python3.9 -m pip install pytest
COPY ./tests /mim/tests
COPY ./config /mim/config
WORKDIR /mim
RUN mkdir local
RUN mkdir local/keyword_features_hyperscan_databases
ENV MIM_OCR_CONFIG_PATH=/mim/config/test_mim_ocr_conf.yaml
RUN python3.9 -m pytest tests