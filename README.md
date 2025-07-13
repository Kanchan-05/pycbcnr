# PyCBCNR

**pycbcnr** is a plugin for [PyCBC](https://github.com/gwastro/pycbc) that enables the generation of gravitational waveforms directly from Numerical Relativity (NR) simulations in the [SXS (Simulating eXtreme Spacetimes)](https://data.black-holes.org/waveforms/index.html) catalog. This allows users to use high-accuracy NR data as input for waveform modeling, injection, or matched filtering in PyCBC-based pipelines.

## Features

- Loads `rhOverM` NR waveforms from the SXS catalog.
- Adjust the starting time w.r.t input `f_ref`.
- Computes the strain \( h(t) \) from spin-weighted spherical harmonics. 
- Rescales waveforms to physical units using input masses and luminosity distance.
- Converts output to `pycbc.types.TimeSeries` with appropriate tapering.

## Installation (for precessing and aligned-spin SXS simulation)

```bash
git clone https://github.com/Kanchan-05/nrpycbc.git
cd pycbcnr
pip install .
```

### Installation (for non-spinning SXS simulation)
```
git clone https://github.com/Kanchan-05/nrpycbc.git
cd pycbcnr
git checkout f64f9fc
pip install .
```

## Dependencies

 - Python ≥ 3.10
 - PyCBC
 - sxs
 - [sxstools](https://github.com/Kanchan-05/sxstools)


## Usage

See `test_nrsxs.ipynb`

## License

This project is licensed under the GNU General Public License v3 (GPLv3). See the LICENSE file for details.

