from setuptools import setup, find_packages

setup(
    name='ogit',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'dulwich',
        'orjson',
    ],
    entry_points={
        'console_scripts': [
            'ogit = ogit.cli:main',
        ],
    },
)