from pathlib import Path

from setuptools import setup
from setuptools import find_packages

BASE_PATH = Path(__file__).parent


def read(path: Path):
    return path.read_text("utf-8")


setup(
    name="smbbackend",
    version=read(BASE_PATH / "VERSION"),
    description="Backend calculations for smb",
    long_description=read(BASE_PATH / "README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/geosolutions-it/smb-backend",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "boto3",
        "psycopg2-binary",
        "pyfcm",
        "pytz",
    ],
    entry_points={
        "console_scripts": [
            "set-lambda-env=smbbackend.awsutils:main_set_lambda_env",
            "convert-spatialite=smbbackend.convertspatialfiles:main",
            "ingest-tracks=smbbackend.standalonehandlers:main",
            "process-tracks-locally=smbbackend.ingestiontester:main"
        ]
    }
)