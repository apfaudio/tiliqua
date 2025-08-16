# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""
Utilities for creating 'bitstream archives', a *.tar.gz archive
containing a bitstream, manifest (describing the contents), as well
as optional firmware images and other resources.

Such archives are a single shareable file that contains all the resources
required to flash a project to a Tiliqua slot (assuming the correct
bootloader and hardware revisions).
"""

import os
import tarfile
import json

from dataclasses import dataclass, field
from fastcrc import crc32
from typing import Optional, List
from tiliqua.types import *
from tiliqua.tiliqua_platform import TiliquaRevision

from rs.manifest.src.lib import OPTION_STORAGE, OPTION_STORAGE_SZ

@dataclass
class BitstreamArchiver:

    """Class for building and writing bitstream archives."""

    build_path: str
    name: str
    sha: str
    hw_rev: TiliquaRevision
    brief: str = ""
    video: Optional[str] = None
    external_pll_config: Optional[ExternalPLLConfig] = None

    _regions: List[MemoryRegion] = field(default_factory=list)
    _manifest: Optional[BitstreamManifest] = None
    _firmware_bin_path: Optional[str] = None

    def __post_init__(self):
        # Ensure build directory exists
        if not os.path.exists(self.build_path):
            os.makedirs(self.build_path)

    @property
    def archive_name(self) -> str:
        return f"{self.name.lower()}-{self.sha}-{self.hw_rev.value}.tar.gz"

    @property
    def archive_path(self) -> str:
        return os.path.join(self.build_path, self.archive_name)

    @property
    def manifest_path(self) -> str:
        return os.path.join(self.build_path, "manifest.json")

    @property
    def bitstream_path(self) -> str:
        return os.path.join(self.build_path, "top.bit")


    def add_firmware_region(self, firmware_bin_path: str, fw_location: FirmwareLocation, fw_offset: int) -> None:
        """
        Add a memory region corresponding to a firmware image.

        Args:
            firmware_bin_path: Path to the firmware binary file
            fw_location: Location of firmware (BRAM, SPIFlash, or PSRAM)
            fw_offset: Offset address for the firmware
        """
        self._firmware_bin_path = firmware_bin_path

        if not os.path.exists(firmware_bin_path):
            print(f"WARNING: Firmware file not found at {firmware_bin_path}")
            return

        # Calculate CRC32 of firmware binary
        fw_crc32 = crc32.bzip2(open(firmware_bin_path, "rb").read())

        # Create a memory region for the firmware
        region = MemoryRegion(
            filename=os.path.basename(firmware_bin_path),
            spiflash_src=None,
            psram_dst=None,
            size=os.path.getsize(firmware_bin_path),
            crc=fw_crc32
        )

        # Set source/destination based on firmware location
        match fw_location:
            case FirmwareLocation.SPIFlash:
                region.spiflash_src = fw_offset
            case FirmwareLocation.PSRAM:
                region.psram_dst = fw_offset
            case FirmwareLocation.BRAM:
                # No offset needed for BRAM
                pass

        self._regions.append(region)

    def add_option_storage_region(self) -> None:
        region = MemoryRegion(
            filename=OPTION_STORAGE,
            spiflash_src=None,
            psram_dst=None,
            size=OPTION_STORAGE_SZ,
            crc=None
        )
        self._regions.append(region)

    def write_manifest(self) -> BitstreamManifest:
        """Write serialized manifest file, return the BitstreamManifest object."""
        self._manifest = BitstreamManifest(
            name=self.name,
            hw_rev=self.hw_rev.platform_class().version_major,
            sha=self.sha,
            brief=self.brief,
            video=self.video if self.video else "<none>",
            external_pll_config=self.external_pll_config,
            regions=self._regions
        )
        self._manifest.write_to_path(self.manifest_path)
        return self._manifest

    def bitstream_exists(self) -> bool:
        return os.path.exists(self.bitstream_path)

    def create_archive(self) -> bool:
        """
        Create a bitstream archive containing the bitstream, manifest, and optionally firmware.
        Returns True if archive was created, False otherwise.
        """
        if not self.bitstream_exists():
            print("\nWARNING: Skipping archive creation - bitstream has not been built")
            return False

        print(f"\nCreating bitstream archive {self.archive_name}...")
        with tarfile.open(self.archive_path, "w:gz") as tar:
            tar.add(self.bitstream_path, arcname="top.bit")
            tar.add(self.manifest_path, arcname="manifest.json")
            if self._firmware_bin_path and os.path.exists(self._firmware_bin_path):
                tar.add(self._firmware_bin_path, arcname="firmware.bin")

        self._print_archive_info()
        print(f"\nSaved to '{self.build_path}/{self.archive_name}'")
        return True

    def _print_archive_info(self):
        """Print information about the created archive."""
        # Print archive contents and size
        print(f"\nContents:")
        with tarfile.open(self.archive_path, "r:gz") as tar:
            for member in tar.getmembers():
                print(f"  {member.name:<12} {member.size//1024:>4} KiB")

        archive_size = os.path.getsize(self.archive_path)
        print(f"\nCompressed bitstream archive size: {archive_size//1024} KiB")

        # Print manifest contents
        with open(self.manifest_path) as f:
            manifest = json.load(f)
        print(f"\nManifest contents:\n{json.dumps(manifest, indent=2)}")

    def validate_existing_bitstream(self) -> bool:
        """
        Validate that an existing bitstream matches the current project.
        Returns True if validation passes, False if it fails.
        """
        if not self.bitstream_exists():
            print(f"\nERROR: No existing bitstream found at {self.bitstream_path}")
            print("You must build the full project at least once before using --fw-only")
            return False

        if not os.path.exists(self.manifest_path):
            print(f"\nERROR: No manifest found at {self.manifest_path}")
            print("You must build the full project at least once before using --fw-only")
            return False

        try:
            with open(self.manifest_path) as f:
                manifest = json.load(f)
                if manifest.get("name") != self.name:
                    print(f"\nERROR: Existing bitstream is for '{manifest.get('name')}', "
                          f"but last build was for '{self.name}'")
                    print("You must build the full project at least once before using --fw-only")
                    return False
                if int(manifest.get("hw_rev")) != self.hw_rev.platform_class().version_major:
                    print(f"\nERROR: Existing bitstream is for hw_rev={manifest.get('hw_rev')}, "
                          f"but last build is for hw_rev={self.hw_rev.platform_class().version_major}")
                    print("You must build the full project at least once before using --fw-only")
                    return False
        except (json.JSONDecodeError, KeyError) as e:
            print("\nERROR: Failed to validate existing manifest:")
            print(f"  {str(e)}")
            return False

        return True
