from setuptools import setup, find_packages

setup(
    name='sofie_DPcomponent',
    version='0.1',
    description=(
        'Implementation of the SOFIE project\'s '
        'Discovery and provisiong component'
    ),
    author='SOFIE Project',
    license='APL 2.0',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=[
        'bson',
        'flask',
        'flask_cors',
        'boto3',
    ],
    zip_safe=False
)