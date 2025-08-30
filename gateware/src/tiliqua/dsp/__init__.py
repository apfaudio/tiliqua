# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""Streaming DSP library with a strong focus on audio."""

import os
from amaranth.lib import stream
from amaranth_future import fixed

# Native 'Audio sample SQ': shape of audio samples from CODEC.
# Signed fixed point, where -1 to +1 represents -8.192V to +8.192V.
ASQ = fixed.SQ(1, int(os.environ.get('TILIQUA_ASQ_WIDTH', '16')) - 1)

# Import basic/frequently used components from individual modules
from .stream_util import *  # noqa: F401
from .vca import *  # noqa: F401
from .oscillators import *  # noqa: F401
from .oneshot import *  # noqa: F401
from .effects import *  # noqa: F401
from .filters import *  # noqa: F401
from .mix import *  # noqa: F401
from .resample import *  # noqa: F401
from .misc import *  # noqa: F401
from .delay_line import *  # noqa: F401

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