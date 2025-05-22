import hydra
import json
from pyprojroot import here
from omegaconf import OmegaConf

conda: "environment.yaml"

# Define paths relative to the project root
data_dir = here("data")

# the workflow configuration file is orchestrated by hydra
# read config with hydra
with hydra.initialize(config_path="conf", version_base=None):
    cfg = hydra.compose(config_name="config", overrides=[])
    print(OmegaConf.to_yaml(cfg))

# read list of variables to parellelize over
years_cfg = OmegaConf.to_container(cfg.query.year, resolve=True)
months_cfg = OmegaConf.to_container(cfg.query.month, resolve=True)
variable_cfg = OmegaConf.to_container(cfg.query.variable, resolve=True)
geographies_cfg = OmegaConf.to_container(cfg.query.geography, resolve=True)

rule all:
    input:
        expand(data_dir / "intermediate/{geography}_environmental_exposure-era5_healthshed_{variable}_{year}_{month}.parquet", 
               geography=geographies_cfg, variable=variable_cfg, year=years_cfg, month=months_cfg)

rule test_api:
    output:
        data_dir / "testing/test_download.grib"
    shell:
        "python src/era5_sandbox/core.py"

rule download_raw_era5:
    output:
        temp(data_dir / "input/{geography}_{year}_{month}.nc")
    shell:
        """
        python src/era5_sandbox/download.py "++query.year={wildcards.year}" "++query.month={wildcards.month}" "++query.geography={wildcards.geography}"
        """

rule spatial_aggregate_raw_era5:
    message:
        "[AGGREGATE] Processing variable '{wildcards.variable}' "
        "for geography '{wildcards.geography}' in {wildcards.year}-{wildcards.month}"
    input:
        data_dir / "input/{geography}_{year}_{month}.nc"
    output:
        data_dir / "intermediate/{geography}_environmental_exposure-era5_healthshed_{variable}_{year}_{month}.parquet"
    params:
        variable="{variable}",
        geography="{geography}"
    script:
        "src/era5_sandbox/aggregate.py"

rule summarize_na_dashboard:
    input:
        rmd = "notes/prototypes/aggregation_visualizer.Rmd",
    output:
        data_dir / "notes/prototypes/figures/{geography}_mean_temperature_{year}.png}",
        data_dir / "notes/prototypes/figures/{geography}_max_temperature_{year}.png}",
        data_dir / "notes/prototypes/figures/{geography}_min_temperature_{year}.png}",
        data_dir / "notes/prototypes/figures/{geography}_mean_dewpoint_{year}.png}",
        data_dir / "notes/prototypes/figures/{geography}_max_dewpoint_{year}.png}",
        data_dir / "notes/prototypes/figures/{geography}_min_dewpoint_{year}.png}",
        data_dir / "notes/prototypes/figures/{geography}_total_precipitation_{year}.png}"
    shell:
        """
        Rscript -e "rmarkdown::render(
            input = './notes/prototypes/aggregation_visualizer.Rmd',
            params = list(
                in_pipeline = TRUE,
                output_files = list(
                raw_na_summary = 'data/testing/raw_na_summary.csv',
                temp_agg = 'data/testing/temperature_agg_long.csv',
                precip_agg = 'data/testing/precipitation_agg_long.csv',
                dewpoint_agg = 'data/testing/dewpoint_agg_long.csv'
                )
            ),
            output_file = tempfile(),
            quiet = FALSE
            )"
        """