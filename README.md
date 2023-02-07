# mim_ocr

## project_goal

The goal of this project is to create a robust and reliable Python library that will be able handle OCR tasks. Several capabilities and features are envisioned:
- Running OCR with different tools such as
  - Tesseract (local)
  - Google Cloud Vision (cloud)
  - AWS OCR (cloud)
  - EasyOCR (local)
- Image Preprocessing, such as:
  - rotation
  - reorientation
- Return OCR results in common data structures
- Finding features in OCR-ed images using
  - regular expressions
  - keyword lists
  - NLP models
- OCR Result visulization
- Running OCR on large data
  - parallelization
  - usage of GPU
- Detecting various features in OCR results

The project was started in the context of manipulating medical data, but is planned to be used in other fields as well.

## Rules for developers

- create automatic tests for your features
- When providing example images for your tests please strip them from personal data. Please also verify that you have permission of the image owner 

***

# Usage

## Requirements
  Required python version 3.9 or 3.10.
  Additional required system packages (tested on ubuntu 20.04):
  - libgl1 
  - libglib2.0-0 
  - tesseract-ocr
  - poppler-utils
  - protobuf-compiler
  Useful requirements:
  - tesseract-ocr-pol (As Tesseract is set by default to Polish language)

The complete setup pipeline starting from raw ubuntu docker image is described in `build/distribution/test_distribution.Dockerfile`

## Installation
  `python -m pip install mim-ocr`

## Running
To run Google OCR locally (both for running and tests) You need to store in local (not commited to git) files a key 
to Google service account in JSON format. The path to this file should be set as a 
GOOGLE_APPLICATION_CREDENTIALS variable.

To run AWS Textract locally (both for running and tests) You need to have properly configured AWS credentials prefferably using environment variables:
* `AWS_ACCESS_KEY_ID` - The access key for your AWS account.
* `AWS_SECRET_ACCESS_KEY` - The secret key for your AWS account.
* `AWS_DEFAULT_REGION` - Specifies the AWS Region to send the request to.
For more information see https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html.

Some features might require creation of a config YAML file with local paths or parameters. Examples of such features:
* Keyword Features finder (requires path to directory where local hyperscan databases are/should be located).
If you want to use such a config file, the path to this file should be set in MIM_OCR_CONFIG_PATH environmental variable.

Example working values can be found at config/test_mim_ocr_conf.yaml.

## Additional Features

Additional features are tested only on python 3.9

### NER_FEATURE

see [NER Feature Readme](docs/ner_feature.md)

# More Information

## Licence
MIT License. See [LICENSE.txt](LICENSE.txt) for details.

# For Maintainers
Building new version of the package: run `python3.9 -m build` from the main folder.

Uploading new version to pypi: `twine upload dist/*` (two newly created files).
