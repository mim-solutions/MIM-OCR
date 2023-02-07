# NER Feature Readme

To use NER-based features (NER_FEATURE from subpackage mim_ocr.heuristics), you need to download xlm-roberta-ner repository, Polish RoBERTa base model and a pretrained model.
A path to the place, where these resources are stored, should be set as NER_RESOURCES_PATH environment variable value, before running the scripts.
```shell
# install optional_requirements
pip install  -r build/optional_requirements/ner_feature_requirements.txt

# clone the repository
git clone https://github.com/mczuk/xlm-roberta-ner

# download the Polish RoBERTa base model
mkdir xlm-roberta-ner/models/roberta_base_fairseq -p
wget https://github.com/sdadas/polish-roberta/releases/download/models/roberta_base_fairseq.zip
unzip roberta_base_fairseq.zip -d xlm-roberta-ner/models/roberta_base_fairseq
rm roberta_base_fairseq.zip

# pre-trained NER model is stored on google drive, to download it, you need to install gdown
pip install gdown

# download the pre-trained model
# the model was trained as described in https://github.com/mczuk/xlm-roberta-ner#train-the-model-from-scratch , with use of updated packages 
gdown 1e0psQazmePJOKUv3VupV4q7KcyZ1_dFM
unzip ner_pretrained_model.zip -d xlm-roberta-ner/models
rm ner_pretrained_model.zip

# set NER_RESOURCES_PATH environment variable value to the path, where downloaded resources are stored
export NER_RESOURCES_PATH="foo/bar/xlm-roberta-ner"
```
NER can be computed either on CPU or CUDA. `NER_FEATURE` from `lib.heuristics.features` uses CPU by default. If `torch.cuda.is_available()`, you can use `NER_FEATURE_CUDA` from `lib.heuristics.features`. 
<br/> To specify, which CUDA device to use, you can initialize `NERFeature` from `lib.heuristics.features_model` with argument `device="cuda:N"`, where `N` specifies the GPU, eg: `NERFeature(device="cuda:0")` or `NERFeature(device="cuda:1")`.
