#!/usr/bin/env python
import json
import re
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

# path to data directory
DPATH_DATA = Path(__file__).parent.parent / "data"

# path to assets directory (for GeoJSON data input/output)
DPATH_ASSETS = Path(__file__).parent / "assets"

# path to generic US states GeoJSON file
FPATH_STATES_JSON_DEFAULT = DPATH_ASSETS / "us_states.json"

# for overriding state names in generic US states GeoJSON file
CUSTOM_STATE_NAME_MAP_DEFAULT = {
    "District of Columbia": "Washington DC",
}

# path to output GeoJSON file
FPATH_OUT_DEFAULT = DPATH_ASSETS / "survey_states.json"


def create_survey_geojson(
    survey_states_and_clusters: Iterable[str],
    fpath_states_json: Path | str = FPATH_STATES_JSON_DEFAULT,
    custom_state_name_map: Optional[dict] = CUSTOM_STATE_NAME_MAP_DEFAULT,
    fpath_out: Optional[Path | str] = FPATH_OUT_DEFAULT,
) -> dict:
    """Create a GeoJSON file for the states and state clusters used in the survey.

    Parameters
    ----------
    survey_states_and_clusters : Iterable[str]
        State and state cluster names to include in the GeoJSON file. State
        cluster names should be in the format "State1, State2, ... (Cluster X)".
    fpath_states_json : Path | str, optional
        Path to GeoJSON file with standard US states.
        By default, will use the one that was
        downloaded from https://github.com/PublicaMundi/MappingAPI/blob/master/data/geojson/us-states.json.
    custom_state_name_map : dict, optional
        Mapping of state names in the original GeoJSON file to state names in survey_states_and_clusters.
    fpath_out : Path | str, optional
        Path to output GeoJSON file.

    Returns
    -------
    dict
        GeoJSON of the survey states and state clusters.

    Raises
    ------
    RuntimeError
        Raised if state clusters cannot be parsed.
    """
    # use default paths if none provided
    if fpath_states_json is None:
        fpath_states_json = FPATH_STATES_JSON_DEFAULT
    if fpath_out is None:
        fpath_out = FPATH_OUT_DEFAULT

    fpath_states_json = Path(fpath_states_json)
    fpath_out = Path(fpath_out)

    # load GeoJSON file
    states_json = json.loads(fpath_states_json.read_text())

    # create mapping for easy access to reference state information
    state_info_map = {
        info["properties"]["name"]: info for info in states_json["features"]
    }

    # apply custom renaming map
    for old_state_name, new_state_name in custom_state_name_map.items():
        state_info_map[new_state_name] = state_info_map.pop(old_state_name)

    # split into clusters and states
    survey_clusters = [
        state for state in survey_states_and_clusters if "Cluster" in state
    ]
    survey_states = [
        state
        for state in survey_states_and_clusters
        if state not in survey_clusters
    ]

    # array of feature dictionaries representing geometries
    # this will be the main content of the final GeoJSON object
    survey_regions_geo_features = []

    # add single states
    for state in survey_states:
        print(f"Adding state {state}")
        state_info = state_info_map[state]
        state_info["id"] = state
        del state_info["properties"]["density"]
        survey_regions_geo_features.append(state_info)

    # add clusters
    for cluster in survey_clusters:

        # get individual state names
        try:
            clustered_states = (
                re.search("(.*) \\(Cluster", cluster).groups()[0].split(", ")
            )
        except Exception as exception:
            raise RuntimeError(
                f"Could not parse states in cluster {cluster}: {exception}"
            )

        print(f"Adding cluster {cluster}")
        cluster_info = None
        for clustered_state in clustered_states:
            print(f"\tAdding state {clustered_state}")

            # first state in the cluster
            if cluster_info is None:
                cluster_info = state_info_map[clustered_state]
                cluster_info["properties"]["name"] = cluster
                cluster_info["id"] = cluster

                # convert into MultiPolygon if needed
                if cluster_info["geometry"]["type"] == "Polygon":
                    cluster_info["geometry"]["type"] = "MultiPolygon"
                    cluster_info["geometry"]["coordinates"] = [
                        cluster_info["geometry"]["coordinates"]
                    ]

            # subsequent states in the cluster
            else:
                state_info = state_info_map[clustered_state]
                if state_info["geometry"]["type"] == "Polygon":
                    to_extend = [
                        state_info_map[clustered_state]["geometry"][
                            "coordinates"
                        ]
                    ]
                else:
                    to_extend = state_info_map[clustered_state]["geometry"][
                        "coordinates"
                    ]
                cluster_info["geometry"]["coordinates"].extend(to_extend)

        del cluster_info["properties"]["density"]
        survey_regions_geo_features.append(cluster_info)

    survey_json = {
        "type": "FeatureCollection",
        "features": survey_regions_geo_features,
    }
    fpath_out.write_text(json.dumps(survey_json, indent=4))
    print(f"GeoJSON file written to {fpath_out}")

    return survey_json


if __name__ == "__main__":

    fpath_df_states = DPATH_DATA / "survey_results" / "sampledesc_state.tsv"
    df_states = pd.read_csv(fpath_df_states, sep="\t")

    create_survey_geojson(df_states["state"].unique())
