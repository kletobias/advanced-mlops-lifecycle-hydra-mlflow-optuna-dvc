import glob
import os

from omegaconf import DictConfig, OmegaConf  # pip install omegaconf


def drop_keys(cfg: DictConfig, keys_to_drop: list[str]) -> DictConfig:
    for key in keys_to_drop:
        cfg.pop(key, None)  # changed
    return cfg  # changed


def process_configs(directory: str, keys_to_drop: list[str]) -> None:
    files = glob.glob(os.path.join(directory, "*.yaml"))  # changed
    for file in files:  # changed
        if os.path.basename(file) == "base.yaml":  # changed
            continue  # changed
        cfg = OmegaConf.load(file)  # changed
        updated = drop_keys(cfg, keys_to_drop)  # changed
        OmegaConf.save(updated, file)  # changed


def main(directory: str, keys_to_drop: list[str]) -> None:
    process_configs(directory, keys_to_drop)


if __name__ == "__main__":
    main(
        directory="/Users/tobias/.local/projects/portfolio_medical_drg_ny/configs/data_versions/",
        keys_to_drop=["file_path_csv", "metadata_file_path"],
    )
