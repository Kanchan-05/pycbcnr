from pycbc.waveform import get_td_waveform
import matplotlib.pyplot as plt
import numpy as np
import sxs

print (sxs.__version__)
hp, hc = get_td_waveform(approximant='nrsxs',
                                 mass1=37,
                                 mass2=32,
                                 delta_t=1.0/4096,
                                 f_lower=20,
                                 inclination=np.pi/3,
                                 coa_phase=np.pi,
                                 distance=400,
                                 sxs_id='SXS:BBH:0305')
plt.plot(hp.sample_times, hp)
plt.xlabel('GPS Time (s)')
plt.ylabel('Strain')
plt.title('Strain vs Time')
plt.grid()
plt.show()