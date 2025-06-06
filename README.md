# Quantile Modeling Pipeline for Genetic Divergence Imputation

Quantile regression pipeline for imputing genetic divergence between pathogen samples using spatiotemporal and host metadata. Includes feature ablation analysis and stratified evaluation.


## Files

- `quantile_modeling_pipeline.py`: Main script that trains a quantile regression model (QRI) and runs ablation analysis across divergence strata.
- `input_data_example.csv`: Synthetic sample input data with required fields and representative values.
- `output_ablation_results.csv`: Output file generated after running the script, containing predictions and evaluation metrics.
- `requirements.txt`: List of required Python packages for reproducibility.

## Input Format

The input dataset should be a CSV file with the following columns:

| Column              | Type    | Description                                             |
|---------------------|---------|---------------------------------------------------------|
| `k80`               | float   | Pairwise genetic divergence (e.g., K80 distance)        |
| `delta_days`        | float   | Time difference between samples (in days)              |
| `family1`, `family2`| string  | Host family names for the two sequences                |
| `state1`, `state2`  | string  | Geographic regions (e.g., US state codes)              |
| `state_distance_km` | float   | Geographic distance between locations in kilometers    |
| `year`              | int     | Year of sample collection                              |

An example is provided in `input_data_example.csv`.

## Usage

To run the full quantile regression pipeline with ablation analysis:

```bash
python quantile_modeling_pipeline.py
