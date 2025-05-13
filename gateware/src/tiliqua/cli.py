# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
Top-level CLI for Tiliqua projects, whether they include an SoC or not.
The set of available commands depends on the specific project.
"""
import argparse
import enum
import logging
import git
import os
import subprocess
import sys
import time

from tiliqua                     import sim, dvi_modeline, tiliqua_pll
from tiliqua.types               import *
from tiliqua.tiliqua_platform    import *
from tiliqua.tiliqua_soc         import TiliquaSoc
from tiliqua.archive             import BitstreamArchiver
from vendor.ila                  import AsyncSerialILAFrontend

class CliAction(str, enum.Enum):
    Build    = "build"
    Simulate = "sim"

# TODO: these arguments would likely be cleaner encapsulated in a dataclass that
# has an instance per-project, that may also contain some bootloader metadata.
def top_level_cli(
    fragment,               # callable elaboratable class (to instantiate)
    video_core=True,        # project requires the video core (framebuffer, DVI output gen)
    path=None,              # project is located here (usually used for finding firmware)
    ila_supported=False,    # project supports compiling with internal ILA
    sim_ports=None,         # project has a list of simulation port names
    sim_harness=None,       # project has a .cpp simulation harness at this path
    argparse_callback=None, # project needs extra CLI flags before argparse.parse()
    argparse_fragment=None # project needs to check args.<custom_flag> after argparse.parse()
    ):

    # Get some repository properties
    repo = git.Repo(search_parent_directories=True)
    repo_sha = repo.head.object.hexsha[:6]

    # Configure logging.
    logging.getLogger().setLevel(logging.DEBUG)

    # Parse arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('--skip-build', action='store_true',
                        help="Perform design elaboration but do not actually build the bitstream.")
    parser.add_argument('--flash', action='store_true',
                        help="Flash bitstream (and firmware if needed) after building it.")
    parser.add_argument('--fs-192khz', action='store_true',
                        help="Force usage of maximum CODEC sample rate (192kHz, default is 48kHz).")

    if video_core:
        parser.add_argument('--modeline', type=str, default='1280x720p60',
                            help="Default video mode if dynamic detection is not available.")

    if sim_ports or issubclass(fragment, TiliquaSoc):
        simulation_supported = True
        parser.add_argument('--trace-fst', action='store_true',
                            help="Simulation: enable dumping of traces to FST file.")
    else:
        simulation_supported = False

    if issubclass(fragment, TiliquaSoc):
        parser.add_argument('--svd-only', action='store_true',
                            help="SoC designs: stop after SVD generation")
        parser.add_argument('--pac-only', action='store_true',
                            help="SoC designs: stop after rust PAC generation")
        parser.add_argument('--fw-only', action='store_true',
                            help="SoC designs: stop after rust FW compilation (optionally re-flash)")
        parser.add_argument("--fw-location",
                            type=FirmwareLocation,
                            default=FirmwareLocation.PSRAM.value,
                            choices=[
                                FirmwareLocation.BRAM.value,
                                FirmwareLocation.SPIFlash.value,
                                FirmwareLocation.PSRAM.value,
                            ],
                            help=(
                                "SoC designs: firmware (.text, .rodata) load strategy. `bram`: firmware "
                                "is baked into bram in the built bitstream. `spiflash`: firmware is "
                                "assumed flashed to spiflash at the provided `--fw-offset`. "
                                "'psram': firmware is assumed already copied to PSRAM (by a bootloader) "
                                "at the provided `--fw-offset`.")
                            )
        parser.add_argument('--fw-offset', type=str, default=None,
                            help="SoC designs: See `--fw-location`.")
        parser.add_argument('--dynamic-modeline', action='store_true',
                            help="SoC designs: video modeline is inherited from bootloader")


    # TODO: is this ok on windows?
    name_default = os.path.normpath(sys.argv[0]).split(os.sep)[2].replace("_", "-").upper()
    parser.add_argument('--name', type=str, default=name_default,
                        help="Bitstream name to display in bootloader and bottom of screen.")
    parser.add_argument('--brief', type=str, default=None,
                        help="Brief description to display in bootloader.")
    parser.add_argument("--hw",
                        type=TiliquaRevision,
                        default=TiliquaRevision.default(),
                        choices=[r.value for r in TiliquaRevision.all()],
                        help=(f"Tiliqua hardware revision (default={TiliquaRevision.default()})"))
    parser.add_argument('--bootaddr', type=str, default="0x0",
                        help="'bootaddr' argument of ecppack (default: 0x0).")
    parser.add_argument('--verbose', action='store_true',
                        help="amaranth: enable verbose synthesis")
    parser.add_argument('--debug-verilog', action='store_true',
                        help="amaranth: emit debug verilog")
    parser.add_argument('--noflatten', action='store_true',
                        help="yosys: don't flatten heirarchy (useful for checking area usage).")
    if ila_supported:
        parser.add_argument('--ila', action='store_true',
                            help="debug: add ila to design, program bitstream after build, poll UART for data.")
        parser.add_argument('--ila-port', type=str, default="/dev/ttyACM0",
                            help="debug: serial port on host that ila is connected to")

    sim_action = [CliAction.Simulate.value] if simulation_supported else []
    parser.add_argument("action", type=CliAction,
                        choices=[CliAction.Build.value] + sim_action)

    if argparse_callback:
        argparse_callback(parser)

    # Print help if no arguments are passed.
    args = parser.parse_args(args=None if sys.argv[1:] else ["--help"])

    if args.action != CliAction.Build:
        assert args.flash == False, "--flash requires 'build' action"

    if argparse_fragment:
        kwargs = argparse_fragment(args)
    else:
        kwargs = {}

    platform_class = args.hw.platform_class()

    audio_clock = platform_class.default_audio_clock
    if video_core:
        if hasattr(args, 'dynamic_modeline') and args.dynamic_modeline:
            kwargs["clock_settings"] = tiliqua_pll.ClockSettings(
                audio_clock.to_192khz() if args.fs_192khz else audio_clock,
                dynamic_modeline=True,
                modeline=None)
        else:
            modelines = dvi_modeline.DVIModeline.all_timings()
            assert args.modeline in modelines, f"error: fixed modeline must be one of {modelines.keys()}"
            kwargs["clock_settings"] = tiliqua_pll.ClockSettings(
                audio_clock.to_192khz() if args.fs_192khz else audio_clock,
                dynamic_modeline=False,
                modeline=modelines[args.modeline])
    else:
        kwargs["clock_settings"] = tiliqua_pll.ClockSettings(
            audio_clock.to_192khz() if args.fs_192khz else audio_clock,
            dynamic_modeline=False,
            modeline=None)

    build_path = os.path.abspath(os.path.join(
        "build", f"{args.name.lower()}-{args.hw.value}"))
    if not os.path.exists(build_path):
        os.makedirs(build_path)

    if issubclass(fragment, TiliquaSoc):
        rust_fw_bin  = "firmware.bin"
        kwargs["firmware_bin_path"] = os.path.join(build_path, rust_fw_bin)
        kwargs["fw_location"] = args.fw_location
        if args.fw_offset is None:
            match args.fw_location:
                case FirmwareLocation.SPIFlash:
                    kwargs["fw_offset"] = 0xb0000
                    print("WARN: firmware loads from SPI flash, but no `--fw-offset` specified. "
                          f"using default: {hex(kwargs['fw_offset'])}")
                case FirmwareLocation.PSRAM:
                    kwargs["fw_offset"] = 0x200000
                    print("WARN: firmware loads from PSRAM, but no `--fw-offset` specified. "
                          f"using default: {hex(kwargs['fw_offset'])}")
        else:
            kwargs["fw_offset"] = int(args.fw_offset, 16)
        kwargs["ui_name"] = args.name
        kwargs["ui_sha"]  = repo_sha
        kwargs["platform_class"] = platform_class

    assert callable(fragment)
    fragment = fragment(**kwargs)

    if args.brief is None:
        if hasattr(fragment, "brief"):
            args.brief = fragment.brief
        else:
            args.brief = ""

    # Instantiate hardware platform class
    hw_platform = platform_class()

    # (only used if firmware comes from SPI flash)
    args_flash_firmware = None

    archiver = BitstreamArchiver(
        build_path=build_path,
        name=args.name,
        sha=repo_sha,
        hw_rev=args.hw,
        brief=args.brief if args.brief is not None else getattr(fragment, "brief", ""),
        video="<none>"
    )

    if video_core:
        archiver.video ="<dynamic>" if kwargs["clock_settings"].dynamic_modeline else args.modeline

    if (kwargs["clock_settings"].dynamic_modeline and
        hw_platform.clock_domain_generator != tiliqua_pll.TiliquaDomainGeneratorPLLExternal):
        raise ValueError(
            "Cannot use --dynamic-modeline on a platform without an external PLL (older than "
            "Tiliqua R4 hardware). Use --modeline instead.")

    if hw_platform.clock_domain_generator == tiliqua_pll.TiliquaDomainGeneratorPLLExternal:
        archiver.external_pll_config = ExternalPLLConfig(
            clk0_hz=kwargs["clock_settings"].frequencies.audio,
            clk1_hz=kwargs["clock_settings"].frequencies.dvi,
            clk1_inherit=kwargs["clock_settings"].dynamic_modeline,
            spread_spectrum=0.01)
        # Ensure PnR/LPF constraints match the external PLL settings above
        hw_platform.resources[('clkex', 0)].clock.frequency = archiver.external_pll_config.clk0_hz
        hw_platform.resources[('clkex', 1)].clock.frequency = archiver.external_pll_config.clk1_hz

    def maybe_flash_firmware(args, kwargs, force_flash=False):
        """Handle `--flash` option where it is supported (at the moment, only XiP)."""
        print()
        match args.fw_location:
            case FirmwareLocation.BRAM:
                print("Note: Firmware is stored in BRAM, it is not possible to flash firmware "
                      "and bitstream separately. The bitstream contains the firmware.")
            case FirmwareLocation.SPIFlash:
                args_flash_firmware = [
                    "sudo", "openFPGALoader", "-c", "dirtyJtag", "-f", "-o", f"{hex(kwargs['fw_offset'])}",
                    "--file-type", "raw", kwargs["firmware_bin_path"]
                ]
                print("SoC is configured for XIP, firmware may be flashed directly to SPI flash by passing "
                      "the bitstream archive to `pdm flash`, or passing `--flash` to build command.")
                if args.flash or force_flash:
                    subprocess.check_call(args_flash_firmware, env=os.environ)
            case FirmwareLocation.PSRAM:
                print("Note: This bitstream expects firmware already copied from SPI flash to PSRAM "
                      "by a bootloader.\nPass the bitstream archive to `pdm flash` to flash it.")
                if args.flash:
                    print("ERROR: direct --flash is only supported for --fw-location=spiflash (XIP). "
                          "Pass the bitstream archive to `pdm flash` instead.")
                    sys.exit(-1)

    if isinstance(fragment, TiliquaSoc):
        # Generate SVD
        svd_path = os.path.join(build_path, "soc.svd")
        fragment.gensvd(svd_path)
        if args.svd_only:
            sys.exit(0)

        # (re)-generate PAC (from SVD)
        rust_fw_root = os.path.join(path, "fw")
        pac_dir = os.path.join(rust_fw_root, "../pac")
        fragment.generate_pac_from_svd(pac_dir=pac_dir, svd_path=svd_path)
        if args.pac_only:
            sys.exit(0)

        # Generate memory.x and some extra constants
        # Finally, build our stripped firmware image.
        fragment.genmem(os.path.join(rust_fw_root, "memory.x"))
        TiliquaSoc.compile_firmware(rust_fw_root, kwargs["firmware_bin_path"])

        # If necessary, add firmware region to bitstream archive.
        archiver.add_firmware_region(
            firmware_bin_path=kwargs["firmware_bin_path"],
            fw_location=args.fw_location,
            fw_offset=kwargs["fw_offset"]
        )

        # Create firmware-only archive if --fw-only specified
        if args.fw_only:
            if not archiver.validate_existing_bitstream():
                sys.exit(1)
            archiver.write_manifest()
            archiver.create_archive()
            maybe_flash_firmware(args, kwargs)
            sys.exit(0)

        # Simulation configuration
        # By default, SoC examples share the same simulation harness.
        if sim_ports is None:
            sim_ports = sim.soc_simulation_ports
            sim_harness = "src/tb_cpp/sim_soc.cpp"

    archiver.write_manifest()

    if args.action == CliAction.Simulate:
        sim.simulate(fragment, sim_ports(fragment), sim_harness,
                     hw_platform, kwargs["clock_settings"], args.trace_fst)
        sys.exit(0)

    if ila_supported and args.ila:
        hw_platform.ila = True
    else:
        hw_platform.ila = False

    if args.action == CliAction.Build:

        build_flags = {
            "build_dir": build_path,
            "verbose": args.verbose,
            "debug_verilog": args.debug_verilog,
            "nextpnr_opts": "--timing-allow-fail",
            "ecppack_opts": f"--freq 38.8 --compress --bootaddr {args.bootaddr}"
        }

        # workaround for https://github.com/YosysHQ/yosys/issues/4451
        build_flags |= {
            "script_after_read": "proc ; splitnets"
        }
        if args.noflatten:
            # workaround for https://github.com/YosysHQ/yosys/issues/4349
            build_flags |= {
                "synth_opts": "-noflatten -run :coarse",
                "script_after_synth":
                    "proc; opt_clean -purge; synth_ecp5 -noflatten -top top -run coarse:",
            }

        print("Building bitstream for", hw_platform.name)

        hw_platform.build(fragment, do_build=not args.skip_build, **build_flags)

        archiver.create_archive()

        if isinstance(fragment, TiliquaSoc):
            maybe_flash_firmware(args, kwargs, force_flash=hw_platform.ila)

        if args.flash or hw_platform.ila:
            bitstream_path = "build/top.bit"
            args_flash_bitstream = ["sudo", "openFPGALoader", "-c", "dirtyJtag",
                                    "-f", bitstream_path]
            # ILA situation always requires flashing, as we want to make sure
            # we aren't getting data from an old bitstream before starting the
            # ILA frontend.
            subprocess.check_call(args_flash_bitstream, env=os.environ)

        if hw_platform.ila:
            vcd_dst = "out.vcd"
            print(f"{AsyncSerialILAFrontend.__name__} listen on {args.ila_port} - destination {vcd_dst} ...")
            frontend = AsyncSerialILAFrontend(args.ila_port, baudrate=115200, ila=fragment.ila)
            frontend.emit_vcd(vcd_dst)

    return fragment
