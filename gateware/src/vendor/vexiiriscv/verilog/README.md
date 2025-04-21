All netlists required for normal project compilation are checked into
this repository, so SpinalHDL/Scala does not need to be installed.

Arguments to CPU generation are hashed to a netlist verilog file. If
the CPU generation flags are changed, the cache of netlists in this
repository will not be hit and `sbt` is invoked to generate a new core.
