from .nrsxs import gen_sxs_waveform

try:
    from ._version import version as __version__
except ModuleNotFoundError:
    __version__ = "" 
