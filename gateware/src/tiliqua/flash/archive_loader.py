# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

import json
import shutil
import tarfile
import tempfile

from pathlib import Path

from ..build.types import BitstreamManifest, RegionType

class ArchiveLoader:
    """
    Extract bitstream archive to a temporary directory
    and parse the contents of its enclosed ``BitstreamManifest``.

    Example usage:
    ```
    with ArchiveLoader("<my_bitstream_archive>.tar.gz") as loader:
        manifest_parsed = loader.manifest
        extracted_folder = loader.tmpdir
    ```
    """

    def __init__(self, archive_path: str):
        self.archive_path = archive_path
        self.manifest: Optional[BitstreamManifest] = None
        self.tmpdir: Optional[Path] = None

    def is_bootloader_archive(self) -> bool:
        if not self.manifest:
            return False
        return any(region.region_type == RegionType.XipFirmware for region in self.manifest.regions)
    def __enter__(self):
        """Extract archive and read manifest."""
        # Create temporary directory and extract everything
        self.tmpdir = Path(tempfile.mkdtemp())
        with tarfile.open(self.archive_path, "r:gz") as tar:
            tar.extractall(self.tmpdir, filter='data')
            manifest_path = self.tmpdir / "manifest.json"
            with open(manifest_path) as f:
                manifest_dict = json.load(f)
                self.manifest = BitstreamManifest.from_dict(manifest_dict)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up temporary directory."""
        if self.tmpdir and self.tmpdir.exists():
            shutil.rmtree(self.tmpdir)
            self.tmpdir = None
            self.manifest = None
