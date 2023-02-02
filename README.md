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
* iDRS Backend (requires path to local iDRS installation and licence files, and postprocessing parameters)
* Keyword Features finder (requires path to directory where local hyperscan databases are/should be located).
If you want to use such a config file, the path to this file should be set in MIM_OCR_CONFIG_PATH environmental variable.

Example working values can be found at config/test_mim_ocr_conf.yaml.

## Additional Features

Additional features are tested only on python 3.9

### iDRS OCR Backend

Requirements:
1. iDRS tar package
2. licences (in the form of linence.txt file)

To use iDRSBackend you need to:
1. Unpack tar package - the unpacked folder will be our `<IDRS_ROOT>`.
<br/>`tar -xf iDRS_16.0.9_Linux64.tar`
2. Install iDRS as described in `<IDRS_ROOT>/documentation/DeveloperGuide.html`, section 3.1.
3. Delete `Common` folder from `<IDRS_ROOT>/samples/cpp`
4. Copy contents of `mim_ocr/backends/IDRS_c_files` into `<IDRS_ROOT>/samples/cpp` folder.
5. In terminal go to `<IDRS_ROOT>/samples/cpp/Image2Json`, create there an empty folder named `debug` and run `make`.
if you are using iDRS 15 and get error: `/usr/bin/ld: cannot find -lidrskrn16` edit `Makefaile` and change `-lidrskrn16` to `-lidrskrn15`.
6. Save absolute path of generated `<IDRS_ROOT>/bin/CppImage2Json16` executable and copy it into `mim_ocr/config/mim_ocr_conf.yaml` file, into `idrs_ocr_script_path` field.
7. Go to `<IDRS_ROOT>/bin` directory and run `./CppImage2Json16 -input foo -output bar -licence ../work/idrs_software_keys_16.inf`.
8. Use command line to input licence keys for at least OCR, PREPRO, DOCUMENT_OUTPUT and IMAGE_FILE modules and choose to save entered informations to a file. The program will finish with error code 1002, but that's not a problem.
9. Copy absolute path `<IDRS_ROOT>/work/idrs_software_keys_16.inf` into `mim_ocr/config/mim_ocr_conf.yaml` file, into field `idrs_licence_path`.

Changes for IDRS_15 - this steps may be made afterwards:

- Use original `Common` directory (not from src)

- For hardware licence (not custom software licence):
    * Run `sudo ./idrs_sentinel_system_init` (just once)
    * Run `./idrs_sentinel_computer_id`
    You get a computer_id code, like: `*1FDBJ9RLQXQN8PJ`
    <br/>If hardware changes and computer_id changes, you contact sales to get a replacement licence free of charge.
    * For each licence key, run
    ```./idrs_sentinel_software_key 01C94D39A80FFE41E99D36152DF8116D11 014A2B6B9C1F0B45E69E365D23F94C3B45 iDRS15_Desktop_15K_license 1 IDRS15_15K_IMAGE_FILE_JBIG2 *1FDBJ9RLQXQN8PJ``` where first you put one licence key at a time, and then you put computer id code generated above

    * You get a long key, such as:
    `*B
UxEWTY7OKNz,Gvgt5LCSfkMEnGNAOauHQ1E4LaRfIBfkzxxdzuzCRH7Vy21oO6KkLvPvN frehJR2HmuXkFOA:k3ahinR,nQh,:Z3KXx8JekRV02KQAfEzs2I,VLiWGnuWcVkWEGOiEW9 2o585mzhJm:uLLH9nRUYt5psYGuPJgRdiZVMdxBUgertn9gHCS3EEEkS3y# "barcode" version "15", no expiration date, exclusive`
<br/>Save it.

    * Run `./CppImage2Json16 -input foo -output bar -licence ../work/idrs_software_keys_16.inf `
    <br/> When prompted
        ```
        License type selection
        2 - IDRS_LICENSE_CUSTOM_SOFTWARE - Custom software
        4 - IDRS_LICENSE_SOFTWARE - Software key protection
        Please enter your iDRS license type: 
        ```
        Choose option 4 and put keys generated above. 

For details see `documentation/DeveloperGuide.html#_licensing_and_protection_types`

The setup is complete, but each time when you want to use IDRSBackend, you need to extend environmental variable `LD_LIBRARY_PATH`: <br/>`export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:<IDRS_ROOT>/lib"`. 
<br/> Or alternatively, you can copy path `<IDRS_ROOT>/lib` into field `idrs_library_path` in `mim_ocr/config/mim_ocr_conf.yaml`.

<br/>

### NER_FEATURE

see [NER Feature Readme](docs/ner_feature.md)

# More Information

## Licence
MIT License. See [LICENSE.txt](LICENSE.txt) for details.

# For Maintainers
Building new version of the package: `python3.9 -m build`
Uploading new version to pypi: `twine upload dist/*`