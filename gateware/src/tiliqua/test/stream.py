# Helpers for Amaranth tests that heavily use streams.
#
# These were lifted from:
# URL: https://github.com/zyp/katsuo-stream
# License: MIT
# Author: Vegard Storheil Eriksen <zyp@jvnv.net>
#

from amaranth.lib import stream
from amaranth.sim import SimulatorContext

async def put(ctx: SimulatorContext, stream: stream.Interface, payload):
    ctx.set(stream.valid, 1)
    ctx.set(stream.payload, payload)
    await ctx.tick().until(stream.ready == 1)
    ctx.set(stream.valid, 0)

async def get(ctx: SimulatorContext, stream: stream.Interface):
    ctx.set(stream.ready, 1)
    payload, = await ctx.tick().sample(stream.payload).until(stream.valid == 1)
    ctx.set(stream.ready, 0)
    return payload
