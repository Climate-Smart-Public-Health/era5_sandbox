"""This module downloads the raw data from CDS and saves it in the local directory"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../../notes/01_download_raw_data.ipynb.

# %% auto 0
__all__ = ['fetch_GADM', 'create_bounding_box', 'download_raw_era5', 'main']

# %% ../../notes/01_download_raw_data.ipynb 4
import os
import hydra
import cdsapi
import geopandas as gpd
from pyprojroot import here
from omegaconf import DictConfig, ListConfig, OmegaConf

try: from era5_sandbox.core import _expand_path
except: from core import _expand_path

# %% ../../notes/01_download_raw_data.ipynb 5
def _validate_query(
        query_body: DictConfig
    )->bool:
    '''
    Check that the query is valid
    '''

    required_keys = ['product_type', 'variable', 'year', 'month', 'day', 'time', 'area', 'data_format', 'download_format']
    if not all([key in query_body.keys() for key in required_keys]):
        print(f"Missing required key in query. Required keys are {required_keys}")
        print("Query validation failed")
        raise ValueError("Invalid query")
    
    if isinstance(query_body['year'], ListConfig):
        query_body['year'] = [str(x).zfill(2) for x in query_body['year']]
    else:
        query_body['year'] = str(query_body['year'])
    if isinstance(query_body['month'], ListConfig):
        query_body['month'] = [str(x).zfill(2) for x in query_body['month']]
    else:
        query_body['month'] = str(query_body['month']).zfill(2)
    
    if isinstance(query_body['day'], ListConfig):
        query_body['day'] = [str(x).zfill(2) for x in query_body['day']]
    else:
        query_body['day'] = str(query_body['day']).zfill(2)

    return OmegaConf.to_container(query_body, resolve=True)

# %% ../../notes/01_download_raw_data.ipynb 6
def fetch_GADM(
        url: str="https://geodata.ucdavis.edu/gadm/gadm4.1/gpkg/gadm41_MDG.gpkg",
        output_file: str="gadm41_MDG.gpkg" # file path to save the GADM data
    )-> str:
    '''
    Fetch the GADM data for Madagascar
    https://geodata.ucdavis.edu/gadm/gadm4.1/gpkg/gadm41_MDG.gpkg
    '''

    output_file_path = _expand_path(output_file)
    if os.path.exists(output_file_path):
        print("GADM data already exists")
        return output_file_path
    
    print("Fetching GADM bounding box data for region")
    os.system("curl --output {} {}".format(output_file, url))
    print("GADM data fetched")
    
    return output_file_path

# %% ../../notes/01_download_raw_data.ipynb 7
def create_bounding_box(
        gadm_file: str, 
        round_to: int = 1, 
        buffer: float = 0.1)->list:
    '''
    Create a bounding box from the GADM data.

    This function reads the GADM data from URL and extracts the bounding box of the region.
    '''

    ground_shape = gpd.read_file(gadm_file, layer = "ADM_ADM_0")

    bbox = ground_shape.total_bounds

    bbox[0] = round(bbox[0], round_to) - buffer
    bbox[1] = round(bbox[1], round_to) - buffer
    bbox[2] = round(bbox[2], round_to) + buffer
    bbox[3] = round(bbox[3], round_to) + buffer
    
    # The bounding box from total_bounds ([min_x, min_y, max_x, max_y]) differs from the CDS API area format ([North, West, South, East]). The CDS API area format is used to specify the area of interest for the data download. The bounding box from total_bounds is in the format ([min_x, min_y, max_x, max_y]). To convert the bounding box to the CDS API area format, we need to rearrange the values as follows:
    bbox = [bbox[3], bbox[0], bbox[1], bbox[2]]

    return bbox


# %% ../../notes/01_download_raw_data.ipynb 8
def download_raw_era5(
        cfg: DictConfig,  # hydra configuration file
        dataset: str = "reanalysis-era5-land", # dataset to download
    )->None:
    '''
    Send the query to the API and download the data
    '''

    # parse the cfg
    testing = cfg.development_mode  # for testing
    output_dir = here("data/input") # output directory
    
    target =os.path.join(_expand_path(output_dir), "{}_{}.nc".format(cfg.query['year'], cfg.query['month']))
    
    client = cdsapi.Client()
    
    query = _validate_query(cfg.query)
    
    # Send the query to the client
    if not testing:
        bounds = create_bounding_box(cfg['gadm_file'])
        query['area'] = bounds
        client.retrieve(dataset, query).download(target)
    else:
        print(f"Testing mode. Not downloading data. Query is {query}")

    print("Done")

# %% ../../notes/01_download_raw_data.ipynb 11
@hydra.main(config_path="../../conf", config_name="config", version_base=None)
def main(cfg: DictConfig) -> None:
    download_raw_era5(cfg=cfg)

# %% ../../notes/01_download_raw_data.ipynb 12
try: from nbdev.imports import IN_NOTEBOOK
except: IN_NOTEBOOK=False

if __name__ == "__main__" and not IN_NOTEBOOK:
    print('Running from __main__ ...')
    
    main()
