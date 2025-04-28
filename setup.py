# setup.py
from setuptools import find_packages, setup

setup(
    name="portfolio_medical_drg_ny_gh",
    version="0.1.0",
    packages=find_packages(include=["dependencies*"]),
)
