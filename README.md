# US Climate Emotions Map
Interactive web app for visualizing US survey results about climate change emotions.


## Development environment

See also the [Contributing Guidelines](CONTRIBUTING.md) for more information.

1. Create a Python environment and install the app and developer dependencies:

    ```bash
    pip install -r requirements.txt
    pip install -r requirements_dev.txt
    ```

2. To set up code formatting and linting, run:
    ```bash
    tox
    ```
    Now, a number of code linters and formatters should automatically run when you try to commit a local change.

3. To install the submodule with the [data](https://github.com/neurodatascience/us_climate_emotions_data):
    ```bash
    git submodule init
    git submodule update
    ```
