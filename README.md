# Quantile Modeling Pipeline for Genetic Divergence Imputation

This repository contains code and a sample dataset for training and evaluating a quantile regression model to impute genetic divergence between pathogen cases. The model incorporates temporal, geographic, and host metadata and supports feature ablation experiments.

<p align="center">
  <img src="assets/framework.jpg" alt=" framework" width="760">
</p>

## Files

- `quantile_modeling_pipeline.py`: Main script that trains a quantile regression model (QRI) and runs ablation analysis across divergence strata.
- `input_data_example.csv`: Synthetic sample input data with required fields and representative values.
- `output_ablation_results.csv`: Output file generated after running the script, containing predictions and evaluation metrics.
- `requirements.txt`: List of required Python packages for reproducibility.


## Input Format

The input dataset should be a CSV file with the following columns:

| Column              | Type    | Description                                             |
|---------------------|---------|---------------------------------------------------------|
| `k80`               | float   | Pairwise genetic divergence                             |
| `delta_days`        | float   | Time difference between samples (in days)               |
| `family1`, `family2`| string  | Host family names for the two sequences                 |
| `state1`, `state2`  | string  | Geographic regions (e.g., US state codes)               |
| `state_distance_km` | float   | Geographic distance between locations in kilometers     |
| `year`              | int     | Year of sample collection                               |

An example is provided in `input_data_example.csv`.

## Usage

Install dependencies using pip:

```bash
pip install -r requirements.txt
```

Then run the pipeline:

```bash
python quantile_modeling_pipeline.py
```

This will train quantile regression models across LOW, MID, and HIGH K80 divergence strata, perform feature ablation analysis, and generate performance metrics.

## Output

The script generates:

- `output_ablation_results.csv`: Contains:
  - True and predicted K80 values at 5%, 50%, and 95% quantiles
  - Residual errors
  - Divergence stratum class
  - Metrics including MAE, RMSE, R², MAPE, and 90% interval coverage

Console output will also include summary statistics and validation metrics for each experiment.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
