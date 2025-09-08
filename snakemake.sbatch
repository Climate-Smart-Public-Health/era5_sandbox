#!/bin/bash
#
#SBATCH -p intermediate # partition (queue)
#SBATCH -c 12 # number of cores 
#SBATCH --mem 250GB # memory 
#SBATCH -t 0-20:00 # time (D-HH:MM)

snakemake --cores 12 --rerun-incomplete

# Rscript -e "rmarkdown::render(
#             input = './notes/prototypes/aggregation_visualizer.Rmd',
#             params = list(
#                 in_pipeline = TRUE,
#                 output_files = list(
#                 raw_na_summary = 'data/testing/raw_na_summary.csv',
#                 temp_agg = 'data/testing/temperature_agg_long.csv',
#                 precip_agg = 'data/testing/precipitation_agg_long.csv',
#                 dewpoint_agg = 'data/testing/dewpoint_agg_long.csv'
#                 )
#             ),
#             output_file = tempfile(),
#             quiet = FALSE
#             )"

