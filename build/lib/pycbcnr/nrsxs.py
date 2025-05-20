import numpy
import lal 
import sxs
import scipy.interpolate
import pycbc.types
import pycbc.waveform.utils 

def gen_sxs_waveform(sxs_id, extrapolation_order=2, download=False, **params): 
    """
    Generate a SXS waveform from the SXS catalog.
    Parameters
    ----------
    sxs_id : str
        The SXS ID of the waveform to load.
    extrapolation_order : int
        The order of the extrapolation to use.
    download : bool
        Whether to download the waveform data if it is not already present.
    params : dict"""

    waveform = sxs.load(f"{sxs_id}/Lev/rhOverM", extrapolation_order=extrapolation_order, download=download)
    metadata = sxs.load(f"{sxs_id}/Lev/metadata.json", download=download)

    # Align to reference time
    ref_time = metadata['reference_time']
    ref_index = waveform.index_closest_to(ref_time)
    waveform = waveform[ref_index:]
    time = waveform.t - waveform.max_norm_time()

    # Compute complex strain from spin-weighted spherical harmonics
    h_total = 0
    inc, phase = params['inclination'], params['coa_phase']
    for l in range(2, 9):
        for m in range(-l, l + 1):
            h_lm = waveform[:, waveform.index(l, m)]
            Y_lm = lal.SpinWeightedSphericalHarmonic(inc, phase, -2, l, m)
            h_total += h_lm * Y_lm

    # Rescale to physical units
    mtotal = params['mass1'] + params['mass2']
    distance = params['distance']
    time *= mtotal * lal.MTSUN_SI
    h_total *= mtotal * lal.MRSUN_SI / (distance * 1e6 * lal.PC_SI)

    # Interpolate onto uniform time grid
    dt = params['delta_t']
    t_uniform = numpy.arange(time[0], time[-1], dt)
    h_interp = scipy.interpolate.interp1d(time, h_total, kind='cubic')(t_uniform)

    # Convert to PyCBC TimeSeries
    hp = pycbc.types.TimeSeries(numpy.real(h_interp), delta_t=dt, epoch=t_uniform[0])
    hc = pycbc.types.TimeSeries(-numpy.imag(h_interp), delta_t=dt, epoch=t_uniform[0])

    # Taper beginning of waveform to avoid edge effects
    taper_duration = 0.1  # seconds
    hp = pycbc.waveform.utils.td_taper(hp, hp.start_time, hp.start_time + taper_duration)
    hc = pycbc.waveform.utils.td_taper(hc, hc.start_time, hc.start_time + taper_duration)

    return hp, hc