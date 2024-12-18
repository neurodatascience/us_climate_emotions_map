# US Climate Emotions Map
Interactive infographic for exploring US survey results on climate change emotions among young people aged 16-25,
from the following study:

["Climate emotions, thoughts, and plans among US adolescents and young adults: a cross-sectional descriptive survey and analysis by political party identification and self-reported exposure to severe weather events."
[Lewandowski, R.E, Clayton, S.D., Olbrich, L., Sakshaug, J.W., Wray, B. et al, (2024)
_The Lancet Planetary Health_, 11 (8)]](https://www.thelancet.com/journals/lanplh/article/PIIS2542-5196(24)00229-8/fulltext)


## Development environment

See also the [Contributing Guidelines](CONTRIBUTING.md) for more information.

To install the app from source:

1. Clone the repository

    > **NOTE:** To use SSH keys to clone the repo and private submodule,
    > run the following command first to ensure that `git://` URls are used automatically:
    > ```bash
    > git config --global url.git@github.com:.insteadOf https://github.com/
    > ```

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
