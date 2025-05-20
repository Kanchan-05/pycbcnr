import numpy
import lal 
import sxs
import scipy.interpolate
import pycbc.types
import pycbc.waveform.utils 

def gen_sxs_waveform(sxs_id, extrapolation_order=2, download=False, **params): 
    """
    Generate a SXS waveform from the SXS catalog, compatible with both old and new SXS API versions.

    Parameters
    ----------
    sxs_id : str
        The SXS ID of the waveform to load.
    extrapolation_order : int
        The order of the extrapolation to use.
    download : bool
        Whether to download the waveform data if it is not already present.
    params : dict
        Dictionary of parameters including mass1, mass2, distance, delta_t, inclination, and coa_phase.

    Returns
    -------
    hp, hc : pycbc.types.TimeSeries
        Plus and cross polarizations of the strain waveform.
    """

    try:
        # Attempt to load for SXS version >2022
        sim = sxs.load(sxs_id,extrapolation_order=extrapolation_order, download=download)
        waveform = sim.H
        ref_time = sim.metadata.reference_time
        
    except Exception:
        # Fall back to older format
        waveform = sxs.load(f"{sxs_id}/Lev/rhOverM", extrapolation_order=extrapolation_order, download=download)
        metadata = sxs.load(f"{sxs_id}/Lev/metadata.json", download=download)
        ref_time = metadata['reference_time']
    

    # Align to reference time
    ref_index = waveform.index_closest_to(ref_time)
    waveform = waveform[ref_index:]
    time = waveform.t - waveform.max_norm_time()

    # Compute complex strain from spin-weighted spherical harmonics
    h_total = 0 
    for (l, m) in waveform.LM: 
        h_lm = waveform[:, waveform.index(l, m)]
        Y_lm = lal.SpinWeightedSphericalHarmonic(params['inclination'], params['coa_phase'], -2, l, m)
        h_total += h_lm * Y_lm

    # Rescale to physical units
    mtotal = params['mass1'] + params['mass2']
    distance = params['distance']
    time *= mtotal * lal.MTSUN_SI
    h_total *= mtotal * lal.MRSUN_SI / (distance * 1e6 * lal.PC_SI)

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