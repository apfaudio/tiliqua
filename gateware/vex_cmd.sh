# rv32im
sbt "Test/runMain vexiiriscv.Generate --xlen=32 --with-rvm --lsu-l1 --lsu-wishbone --lsu-l1-wishbone --fetch-l1 --fetch-wishbone --reset-vector 0x20200000 --region base=00000000,size=80000000,main=1,exe=1 --region base=F0000000,size=10000,main=0,exe=0"

# rv32im a bit faster
sbt "Test/runMain vexiiriscv.Generate --xlen=32 --with-rvm --lsu-l1 --lsu-wishbone --lsu-l1-wishbone --fetch-l1 --fetch-wishbone --reset-vector 0x20200000 --region base=00000000,size=80000000,main=1,exe=1 --region base=F0000000,size=10000,main=0,exe=0 --with-btb --with-gshare --with-ras --regfile-async"

# rv32im even faster
sbt "Test/runMain vexiiriscv.Generate --xlen=32 --with-rvm --lsu-l1 --lsu-wishbone --lsu-l1-wishbone --fetch-l1 --fetch-wishbone --reset-vector 0x20200000 --region base=00000000,size=80000000,main=1,exe=1 --region base=F0000000,size=10000,main=0,exe=0 --with-btb --with-gshare --with-ras --regfile-async --with-aligner-buffer --with-dispatcher-buffer --with-late-alu"

# rv32im even faster fat cache
sbt "Test/runMain vexiiriscv.Generate --xlen=32 --with-rvm --lsu-l1 --lsu-wishbone --lsu-l1-wishbone --fetch-l1 --fetch-wishbone --reset-vector 0x20200000 --region base=00000000,size=80000000,main=1,exe=1 --region base=F0000000,size=10000,main=0,exe=0 --with-btb --with-gshare --with-ras --regfile-async --with-aligner-buffer --with-dispatcher-buffer --with-late-alu --lsu-l1-ways=2 --fetch-l1-ways=2"

# rv32imafc
sbt "Test/runMain vexiiriscv.Generate --xlen=32 --with-btb --fma-reduced-accuracy --fpu-ignore-subnormal --lsu-l1-ways=2 --with-rva --with-rvm --with-rvc --with-rvf --lsu-l1 --lsu-wishbone --lsu-l1-wishbone --fetch-l1 --fetch-wishbone --reset-vector 0x20200000 --region base=00000000,size=80000000,main=1,exe=1 --region base=F0000000,size=10000,main=0,exe=0 --region base=A0000000,size=10000,main=0,exe=0"

# rv32imafc boost
sbt "Test/runMain vexiiriscv.Generate --xlen=32 --with-btb --with-gshare --with-ras --regfile-async --with-aligner-buffer --with-dispatcher-buffer --with-late-alu --lsu-l1-ways=2 --fetch-l1-ways=2 --fma-reduced-accuracy --fpu-ignore-subnormal --lsu-l1-ways=2 --with-rva --with-rvm --with-rvc --with-rvf --lsu-l1 --lsu-wishbone --lsu-l1-wishbone --fetch-l1 --fetch-wishbone --reset-vector 0x20200000 --region base=00000000,size=80000000,main=1,exe=1 --region base=F0000000,size=10000,main=0,exe=0 --region base=A0000000,size=10000,main=0,exe=0"
