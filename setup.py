"""Setup.py for Collocator."""
from setuptools import setup, find_packages

# List of requirements
requirements = []  # This could be retrieved from requirements.txt
# Package (minimal) configuration
setup(
    name="Collocator",
    version="0.1.0",
    description="A FastAPI webservices for ngrams",
    packages=find_packages(),  # __init__.py folders search
    install_requires=requirements,
)
