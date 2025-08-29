# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""Streaming DSP library with a strong focus on audio."""

from amaranth.lib import stream
from ..eurorack_pmod import ASQ  # hardware native fixed-point sample type

# Import basic/frequently used components from individual modules
from .stream_util import *
from .vca import *
from .oscillators import *
from .oneshot import *
from .effects import *
from .filters import *
from .mix import *
from .resample import *
from .misc import *
from .delay_line import *

# Re-export specialized modules with qualified access
from . import mac
from . import fft
from . import spectral
from . import delay_effect
from . import block
from . import complex

# Dummy values used to hook up to unused stream in/out ports, so they don't block forever
ASQ_READY = stream.Signature(ASQ, always_ready=True).flip().create()
ASQ_VALID = stream.Signature(ASQ, always_valid=True).create()

# Re-export all components for easy access
# (Individual components are imported via * from their modules)
__all__ = [
    # Specialized modules (qualified access)
    'mac', 'fft', 'spectral', 'delay_effect', 'block', 'complex',
    # Constants
    'ASQ_READY', 'ASQ_VALID'
]