# src/utils/helpers.py

import pandas as pd
import yaml


def load_excel_dataset(path):
    """
    Load dataset from Excel
    """
    return pd.read_excel(path)


def flatten(list_of_lists):
    """
    Flatten nested list
    """
    return [item for sublist in list_of_lists for item in sublist]


def load_yaml_config(path):
    """
    Load YAML config file
    """
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_results(results, path):
    """
    Save results to CSV
    """
    df = pd.DataFrame(results)
    df.to_csv(path, index=False)
