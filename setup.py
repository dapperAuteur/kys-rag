# setup.py
from setuptools import setup, find_packages

setup(
    name="science_decoder",
    version="0.1",
    description="A RAG tool for analyzing scientific articles and studies",
    author="BAM",
    author_email="a@awews.com",
    packages=find_packages(),  # Automatically finds all packages marked by __init__.py
    install_requires=[
        "fastapi>=0.109.2",
        "uvicorn>=0.27.1",
        "motor>=3.3.2",
        "pydantic>=2.0.0",
        "transformers",
        "torch",
        "beautifulsoup4>=4.12.3",
        "aiohttp>=3.9.5",
        "python-multipart>=0.0.9",
        # Add other dependencies from your requirements.txt
    ],
    python_requires=">=3.11",  # Specify minimum Python version
)