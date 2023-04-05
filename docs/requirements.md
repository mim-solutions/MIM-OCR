[build/requirements.txt](../build/requirements.txt) - the main place for tracking dependencies. If changed, please reflect the changes in the [pyproject.toml](../pyproject.toml) file as well.

[build/dev_requirements.txt](../build/dev_requirements.txt) - tools for working with the repository; they are not needed to use the project as-is.

[build/base_image/base_requirements.txt](../build/base_image/base_requirements.txt) - dependecies that are presumed to be stable. They are installed during creation of the base Docker image. If changed, please reflect the changes in the [pyproject.toml](../pyproject.toml) file as well. To rebuild the base Docker image, trigger manually the ["Build Base Image"](../../../actions/workflows/prepare-base-image.yml) workflow.

[build/optional_requirements](../build/optional_requirements) - requirements for the optional features. If a new optional feature is implemented and it requires additional dependencies, please create a separate requirements file in this folder and include its installation in the [pytest.yml](../.github/workflows/pytest.yml) workflow definition.
