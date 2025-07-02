import os
import numpy
import lal 
import sxs
import scipy.interpolate
import pycbc.types
import pycbc.waveform.utils 

def get_sxs_cache_path():
    """Determine the SXS cache path, handling older and newer conventions."""
    for path in [os.path.expanduser("~/.sxs/cache"), os.path.expanduser("~/.cache/sxs")]:
        if os.path.exists(path):
            return path
    raise FileNotFoundError("Could not find SXS cache directory in standard locations.")

def gen_sxs_waveform(sxs_id, extrapolation="N2", download=False, **params): 
    """
    Generate a SXS waveform from the SXS catalog, compatible with both old and new SXS API versions.

    Parameters
    ----------
    sxs_id : str
        The SXS simulation ID.
    extrapolation_order : int
        The order of the extrapolation to use.
    download : bool
        Whether to download the waveform data if it is not already present.
    params : dict
        Parameters: mtotal (solar masses), distance (Mpc), delta_t (s), f_ref (Hz),
        inclination (rad), coa_phase (rad).
    Returns
    -------
    hp, hc : pycbc.types.TimeSeries
        Plus and cross polarizations of the strain.
    """

    # Attempt to load for SXS version >2022
    sim = sxs.load(sxs_id,extrapolation=extrapolation, download=download)

    from sxstools.quantities import get_dynamics_from_h5, get_t_ref_from_dynamics_and_freq, get_NR_ref_quantities_at_t_ref
    from sxstools.coordinate_transform import CoordinateTransform

    # Load dynamics
    cache_path = get_sxs_cache_path()
    horizons = sim.horizons
    horizons_file_path = os.path.join(cache_path, sim.location + ":Horizons.h5")
    dynamics = get_dynamics_from_h5(horizons_file_path)
    
    # Get the reference time for the waveform
    tref = get_t_ref_from_dynamics_and_freq(
        dynamics, f_ref=params["f_ref"], Mtotal=params["mtotal"], t_junk=100
    )

    # Get the reference parameters in the NR reference frame
    NR_ref_params = get_NR_ref_quantities_at_t_ref(dynamics=dynamics, t_ref=tref)

    t_operator = CoordinateTransform(NR_ref_parames=NR_ref_params,
                                dynamics=dynamics,
                                waveform_modes=sim.H,
                                )
    t_operator.transform()
    waveform = t_operator.waveform_modes_rot_xyz
    ref_time = t_operator.t_ref
    

    # Align to reference time
    # NOTE for future: The ref_index could be found over an interpolated time grid
    ref_index = numpy.argmin(abs(t_operator.waveform_modes_rot_xyz.t - ref_time))
    waveform_sliced = waveform[ref_index:]
    time = waveform_sliced.t - waveform_sliced.max_norm_time()

    # Compute complex strain from spin-weighted spherical harmonics
    h_total = None 
    for (l, m) in waveform_sliced.LM: 
        h_lm = waveform_sliced.data[:, waveform_sliced.index(l, m)]
        Y_lm = lal.SpinWeightedSphericalHarmonic(params['inclination'], params['coa_phase'], -2, l, m)
        if h_total is None:
            h_total = Y_lm * h_lm
        else:
            h_total += Y_lm * h_lm 

    # NOTE: The polarization angle has to be included so that the waveform transforms correctly
    # Since we have not corrected for the polarization angle, we may estimate it incorrectly in the analysis

    # Rescale to physical units
    time *= params['mtotal'] * lal.MTSUN_SI
    h_total *= params['mtotal'] * lal.MRSUN_SI / (params['distance'] * 1e6 * lal.PC_SI)

    # Interpolate onto uniform time grid 
    t_uniform = numpy.arange(time[0], time[-1], params['delta_t'])
    h_interp = scipy.interpolate.interp1d(time, h_total, kind='cubic')(t_uniform)

    # Convert to PyCBC TimeSeries
    hp = pycbc.types.TimeSeries(numpy.real(h_interp), delta_t=params['delta_t'], epoch=t_uniform[0])
    hc = pycbc.types.TimeSeries(-numpy.imag(h_interp), delta_t=params['delta_t'], epoch=t_uniform[0])

    # Taper beginning of waveform to avoid edge effects
    taper_duration = 0.1  # seconds
    hp = pycbc.waveform.utils.td_taper(hp, hp.start_time, hp.start_time + taper_duration)
    hc = pycbc.waveform.utils.td_taper(hc, hc.start_time, hc.start_time + taper_duration)

    return hp, hc