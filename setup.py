# setup.py
from setuptools import setup, find_packages

setup(
    name="portfolio_medical_drg_ny_gh",
    version="0.1.0",
    packages=find_packages(include=["dependencies*"]),
)
