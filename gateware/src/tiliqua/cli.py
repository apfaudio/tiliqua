# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
Top-level CLI for Tiliqua projects, whether they include an SoC or not.
The set of available commands depends on the specific project.
"""
import argparse
import enum
import git
import logging
import json
import os
import subprocess
import sys
import time
import tarfile
from datetime import datetime

from fastcrc import crc32

from tiliqua                     import sim, video
from tiliqua.types               import *
from tiliqua.tiliqua_platform    import *
from tiliqua.tiliqua_soc         import TiliquaSoc
from vendor.ila                  import AsyncSerialILAFrontend

class CliAction(str, enum.Enum):
    Build    = "build"
    Simulate = "sim"

def maybe_flash_firmware(args, kwargs, force_flash=False):
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

    # Configure logging.
    logging.getLogger().setLevel(logging.DEBUG)

    # Parse arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('--flash', action='store_true',
                        help="Flash bitstream (and firmware if needed) after building it.")
    parser.add_argument('--fs-192khz', action='store_true',
                        help="Force usage of maximum CODEC sample rate (192kHz, default is 48kHz).")

    if video_core:
        parser.add_argument('--resolution', type=str, default="1280x720p60",
                            help="DVI resolution - (default: 1280x720p60)")
        parser.add_argument('--rotate-90', action='store_true',
                            help="Rotate DVI out by 90 degrees")

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

    kwargs = {}

    if video_core:
        assert args.resolution in video.DVI_TIMINGS, f"error: video resolution must be one of {video.DVI_TIMINGS.keys()}"
        dvi_timings = video.DVI_TIMINGS[args.resolution]
        kwargs["dvi_timings"] = dvi_timings
        if args.rotate_90:
            kwargs["video_rotate_90"] = True

    platform_class = {
        TiliquaRevision.R2:    TiliquaR2SC2Platform,
        TiliquaRevision.R2SC3: TiliquaR2SC3Platform,
        TiliquaRevision.R3:    TiliquaR3SC3Platform,
        TiliquaRevision.R4:    TiliquaR4SC3Platform,
    }[args.hw]

    audio_clock = platform_class.default_audio_clock
    kwargs["clock_settings"] = tiliqua_pll.clock_settings(
        audio_clock.to_192khz() if args.fs_192khz else audio_clock,
        video_timings=dvi_timings if video_core else None)

    if issubclass(fragment, TiliquaSoc):
        rust_fw_bin  = "firmware.bin"
        rust_fw_root = os.path.join(path, "fw")
        kwargs["firmware_bin_path"] = os.path.join(rust_fw_root, rust_fw_bin)
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
        kwargs["ui_sha"]  = repo.head.object.hexsha[:6]
        kwargs["platform_class"] = platform_class

    if argparse_fragment:
        kwargs = kwargs | argparse_fragment(args)

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

    build_path = "build"
    if not os.path.exists(build_path):
        os.makedirs(build_path)

    manifest_path = os.path.join(build_path, "manifest.json")

    def write_manifest(regions):
        if hw_platform.clock_domain_generator == tiliqua_pll.TiliquaDomainGeneratorPLLExternal:
            settings = kwargs["clock_settings"]
            external_pll_config = ExternalPLLConfig(
                    clk0_hz=settings.frequencies.audio,
                    clk1_hz=settings.frequencies.dvi,
                    spread_spectrum=0.01)
        else:
            external_pll_config = None
        manifest = BitstreamManifest(
            magic=BITSTREAM_MANIFEST_MAGIC,
            name=args.name,
            hw_rev=hw_platform.version_major,
            sha=repo.head.object.hexsha[:6],
            brief=args.brief,
            video=args.resolution if hasattr(args, 'resolution') else "<none>",
            external_pll_config=external_pll_config,
            regions=regions
        )
        def cleandict(d):
            """Remove all k, v pairs where v == None."""
            if isinstance(d, dict):
                return {k: cleandict(v) for k, v in d.items() if v is not None}
            elif isinstance(d, list):
                return [cleandict(v) for v in d]
            else:
                return d
        with open(manifest_path, "w") as f:
            # Drop all keys with None values (optional fields)
            f.write(json.dumps(cleandict(manifest.to_dict())))
        return manifest

    def create_bitstream_archive():
        archive_name = f"{args.name.lower()}-{repo.head.object.hexsha[:6]}-{args.hw.value}.tar.gz"
        archive_path = os.path.join(build_path, archive_name)
        bitstream_path = "build/top.bit"
        # Check if we have a bitstream
        has_bitstream = os.path.exists(bitstream_path)
        if not has_bitstream:
            print("\nWARNING: Skipping archive creation - bitstream has not been built")
            return
        print(f"\nCreating bitstream archive {archive_name}...")
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(bitstream_path, arcname="top.bit")
            tar.add(manifest_path, arcname="manifest.json")
            if isinstance(fragment, TiliquaSoc):
                tar.add(kwargs["firmware_bin_path"], arcname="firmware.bin")
        # Print archive contents and size
        print(f"\nContents:")
        with tarfile.open(archive_path, "r:gz") as tar:
            for member in tar.getmembers():
                print(f"  {member.name:<12} {member.size//1024:>4} KiB")
        archive_size = os.path.getsize(archive_path)
        print(f"\nCompressed bitstream archive size: {archive_size//1024} KiB")

        # Print manifest contents
        with open(manifest_path) as f:
            manifest = json.load(f)
        print(f"\nManifest contents:\n{json.dumps(manifest, indent=2)}")

    def validate_existing_bitstream(args, manifest_path="build/manifest.json"):
        """
        Validate that an existing bitstream matches the current project when using --fw-only.
        Returns True if validation passes, False if it fails.
        """
        if not os.path.exists("build/top.bit"):
            print("\nERROR: No existing bitstream found at build/top.bit")
            print("You must build the full project at least once before using --fw-only")
            return False
        if not os.path.exists(manifest_path):
            print("\nERROR: No manifest found at build/manifest.json")
            print("You must build the full project at least once before using --fw-only") 
            return False
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
                if manifest.get("name") != args.name:
                    print(f"\nERROR: Existing bitstream is for '{manifest.get('name')}', "
                          f"but current project is '{args.name}'")
                    print("You must build the full project at least once before using --fw-only")
                    return False
        except (json.JSONDecodeError, KeyError) as e:
            print("\nERROR: Failed to validate existing manifest:")
            print(f"  {str(e)}")
            return False
        return True

    if isinstance(fragment, TiliquaSoc):
        # Generate SVD
        svd_path = os.path.join(rust_fw_root, "soc.svd")
        fragment.gensvd(svd_path)
        if args.svd_only:
            sys.exit(0)

        # (re)-generate PAC (from SVD)
        TiliquaSoc.regenerate_pac_from_svd(svd_path)
        if args.pac_only:
            sys.exit(0)

        # Generate memory.x and some extra constants
        # Finally, build our stripped firmware image.
        fragment.genmem(os.path.join(rust_fw_root, "memory.x"))
        fragment.genconst("src/rs/lib/src/generated_constants.rs")
        TiliquaSoc.compile_firmware(rust_fw_root, rust_fw_bin)

        fw_crc32 = crc32.bzip2(open(kwargs["firmware_bin_path"], "rb").read())
        regions = [
            MemoryRegion(
                filename=os.path.basename(kwargs["firmware_bin_path"]),
                spiflash_src=None,
                psram_dst=None,
                size=os.path.getsize(kwargs["firmware_bin_path"]),
                crc=fw_crc32
            )
        ]
        match args.fw_location:
            case FirmwareLocation.SPIFlash:
                regions[-1].spiflash_src = kwargs["fw_offset"]
            case FirmwareLocation.PSRAM:
                regions[-1].psram_dst = kwargs["fw_offset"]

        # Create firmware-only archive if --fw-only specified
        if args.fw_only:
            if not validate_existing_bitstream(args):
                sys.exit(1)
            write_manifest(regions)
            create_bitstream_archive()
            maybe_flash_firmware(args, kwargs)
            sys.exit(0)
        else:
            write_manifest(regions)

        # Simulation configuration
        # By default, SoC examples share the same simulation harness.
        if sim_ports is None:
            sim_ports = sim.soc_simulation_ports
            sim_harness = "src/tb_cpp/sim_soc.cpp"
    else:
        write_manifest(regions=[])

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

        hw_platform.build(fragment, **build_flags)

        create_bitstream_archive()

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
