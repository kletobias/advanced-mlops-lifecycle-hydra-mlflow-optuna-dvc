# setup.py
from setuptools import find_packages, setup

setup(
    name="portfolio_medical_drg_ny_gh_ny_311",
    version="0.1.1",
    packages=find_packages(include=["dependencies*"]),
)
