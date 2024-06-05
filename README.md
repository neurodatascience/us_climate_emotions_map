# US Climate Emotions Map
Interactive web app for visualizing US survey results about climate change emotions.


## Development environment

See also the [Contributing Guidelines](CONTRIBUTING.md) for more information.

To install the app from source:

1. Clone the repository
    ```bash
    git clone https://github.com/neurodatascience/us_climate_emotions_map.git

    # Or, to clone and directly install the data submodule all at once:
    git clone --recurse-submodules --branch main https://github.com/neurodatascience/us_climate_emotions_map.git
    ```

2. Create a Python environment and install the app and developer dependencies:

    ```bash
    pip install -r requirements.txt
    pip install -r requirements_dev.txt
    ```

2. To set up code formatting and linting, run:
    ```bash
    tox
    ```
    Now, a number of code linters and formatters should automatically run when you try to commit a local change.

3. To install the [data](https://github.com/neurodatascience/us_climate_emotions_data) submodule, if you did not do so in step 1:
    ```bash
    git submodule init
    git submodule update
    ```

    To update the submodule in your local clone to the latest revision in this repository:
    ```bash
    git submodule update
    ```

To launch the app locally:
```bash
python -m climate_emotions_map.app
```

## Deployment

This dashboard will be deployed as a docker container.
Because the data are not public, we will provide them to the docker
container as a volume. The Makefile helps you set this up.

First setup:
```bash
make setup
```

This will
- initialize the submodule with the data if you haven't already
- create a new docker volume called `climate_data`
- copy the data from the submodule to the volume so we can reuse it

Deploy the app:
```bash
docker compose up -d
```

This will:
- build the docker image
- mount the `climate_data` volume to the app
- start the dashboard in the docker container

You can then interact with the app at `localhost:8050` as before.
