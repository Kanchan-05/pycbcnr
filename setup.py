from setuptools import Extension, setup, Command, find_packages

VERSION = '0.2'

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='pynr',
    version=VERSION,
    description='A waveform plugin for PyCBC and loading NR waveforms from the catalogues',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Kanchan Soni',
    author_email='kanchsoni03@gmail.com',
    url='https://github.com/Kanchan-05/pynr',
    keywords=['gravitational waves', 'pycbc', 'sxs', 'rit', 'maya', 'nr data'],
    packages=find_packages(),
    python_requires='>=3.8',

    entry_points={
        "pycbc.waveform.td": [
        "nrsxs = pycbcnr.nrsxs:gen_sxs_waveform", 
    ],
    },

    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Astronomy',
        'Topic :: Scientific/Engineering :: Physics',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],

    install_requires=[
        "pycbc",
        "sxs<=2022.5.6",
        "numpy",
        "scipy",
        "h5py",
        "glob2",
        "jsons",
        "lalsuite",
        "romspline",
        "requests_cache"
    ]
)