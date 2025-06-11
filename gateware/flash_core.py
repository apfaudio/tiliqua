#!/usr/bin/env python3
"""
Core flashing logic for Tiliqua bitstream archives.
This module contains the platform-agnostic logic that can be used
both by the command-line tool and the web interface via Pyodide.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Protocol
from dataclasses import dataclass

# Flash memory map constants
N_MANIFESTS = 8
SLOT_BITSTREAM_BASE = 0x100000
SLOT_SIZE = 0x100000
MANIFEST_SIZE = 1024
BOOTLOADER_BITSTREAM_ADDR = 0x000000
FIRMWARE_BASE_SLOT0 = 0x1B0000
FLASH_PAGE_SIZE = 1024


class FlashCommand(Protocol):
    """Protocol for flash commands."""
    def execute(self) -> None:
        """Execute the flash command."""
        ...


@dataclass
class FlashOperation:
    """Represents a flash operation to be executed."""
    filename: str
    offset: int
    file_type: str
    data: bytes
    skip_reset: bool = True
    
    def to_args(self) -> List[str]:
        """Convert to openFPGALoader arguments."""
        args = [
            "-c", "dirtyJtag",
            "-f",
            "-o", f"0x{self.offset:x}",
            "--file-type", self.file_type,
        ]
        if self.skip_reset:
            args.append("--skip-reset")
        return args


@dataclass
class Region:
    """Flash memory region descriptor."""
    addr: int
    size: int
    name: str

    @property
    def aligned_size(self) -> int:
        """Return size aligned up to page boundary."""
        return (self.size + FLASH_PAGE_SIZE - 1) & ~(FLASH_PAGE_SIZE - 1)

    @property
    def end_addr(self) -> int:
        """Return end address (exclusive)."""
        return self.addr + self.aligned_size

    def __lt__(self, other):
        """Enable sorting regions by address."""
        return self.addr < other.addr

    def __str__(self) -> str:
        return (f"{self.name}:\n"
                f"    start: 0x{self.addr:x}\n"
                f"    end:   0x{self.addr + self.aligned_size - 1:x}")


class FlashCore:
    """Core flashing logic for Tiliqua bitstream archives."""
    
    def __init__(self):
        self.operations: List[FlashOperation] = []
        self.regions: List[Region] = []
        self.manifest: Optional[Dict] = None
        
    def validate_hardware(self, hw_rev_attached: int, hw_rev_manifest: int) -> Tuple[bool, str]:
        """Validate hardware revision compatibility."""
        if hw_rev_attached != hw_rev_manifest:
            return False, f"Aborting: attached Tiliqua (hw=r{hw_rev_attached}) does not match archive (hw=r{hw_rev_manifest})."
        return True, ""
    
    def check_xip_firmware(self, manifest: Dict) -> Tuple[bool, Optional[int]]:
        """Check if manifest contains XIP firmware."""
        for region in manifest.get("regions", []):
            if region.get("spiflash_src") is not None:
                return True, region["spiflash_src"]
        return False, None
    
    def validate_slot_assignment(self, has_xip: bool, slot: Optional[int], xip_offset: Optional[int]) -> Tuple[bool, str]:
        """Validate slot assignment for the firmware type."""
        if has_xip and slot is not None:
            return False, (f"Error: XIP firmware bitstreams must be flashed to bootloader slot\n"
                          f"Remove --slot argument to flash at 0x0 with firmware at 0x{xip_offset:x}")
        elif not has_xip and slot is None:
            return False, "Error: Must specify slot for non-XIP firmware bitstreams"
        return True, ""
    
    def check_region_overlaps(self, regions: List[Region], slot: Optional[int] = None) -> Tuple[bool, str]:
        """Check for overlapping regions in flash commands and slot boundaries."""
        # For non-XIP firmware, check if any region exceeds its slot
        if slot is not None:
            for region in regions:
                slot_start = (region.addr // SLOT_SIZE) * SLOT_SIZE
                slot_end = slot_start + SLOT_SIZE
                if region.end_addr > slot_end:
                    return (True, f"Region '{region.name}' exceeds slot boundary: "
                                 f"ends at 0x{region.end_addr:x}, slot ends at 0x{slot_end:x}")

        # Sort by start address and check for overlaps
        sorted_regions = sorted(regions)
        for i in range(len(sorted_regions) - 1):
            curr_end = sorted_regions[i].end_addr
            next_start = sorted_regions[i + 1].addr
            if curr_end > next_start:
                return (True, f"Overlap detected between '{sorted_regions[i].name}' (ends at 0x{curr_end:x}) "
                              f"and '{sorted_regions[i+1].name}' (starts at 0x{next_start:x})")

        return (False, "")
    
    def prepare_xip_firmware(self, manifest: Dict, files: Dict[str, bytes]) -> None:
        """Prepare XIP firmware flashing operations."""
        self.operations = []
        self.regions = []
        
        # Bootloader bitstream
        bitstream_data = files.get("top.bit")
        if not bitstream_data:
            raise ValueError("top.bit not found in archive")
            
        self.operations.append(FlashOperation(
            filename="top.bit",
            offset=BOOTLOADER_BITSTREAM_ADDR,
            file_type="bit",
            data=bitstream_data
        ))
        
        self.regions.append(Region(
            BOOTLOADER_BITSTREAM_ADDR,
            len(bitstream_data),
            'bootloader bitstream'
        ))
        
        # XIP firmware regions
        for region_info in manifest.get("regions", []):
            if "filename" not in region_info:
                continue
                
            if region_info.get("spiflash_src") is not None:
                region_data = files.get(region_info["filename"])
                if not region_data:
                    continue
                    
                self.operations.append(FlashOperation(
                    filename=region_info["filename"],
                    offset=region_info["spiflash_src"],
                    file_type="raw",
                    data=region_data
                ))
                
                self.regions.append(Region(
                    region_info["spiflash_src"],
                    region_info["size"],
                    f"firmware '{region_info['filename']}'"
                ))
    
    def prepare_psram_firmware(self, manifest: Dict, files: Dict[str, bytes], slot: int) -> Dict:
        """Prepare PSRAM firmware flashing operations. Returns updated manifest."""
        self.operations = []
        self.regions = []
        
        # Calculate addresses for this slot
        slot_base = SLOT_BITSTREAM_BASE + (slot * SLOT_SIZE)
        bitstream_addr = slot_base
        manifest_addr = (slot_base + SLOT_SIZE) - MANIFEST_SIZE
        firmware_base = FIRMWARE_BASE_SLOT0 + (slot * SLOT_SIZE)
        
        # Bitstream
        bitstream_data = files.get("top.bit")
        if not bitstream_data:
            raise ValueError("top.bit not found in archive")
            
        self.operations.append(FlashOperation(
            filename="top.bit",
            offset=bitstream_addr,
            file_type="bit",
            data=bitstream_data
        ))
        
        self.regions.append(Region(bitstream_addr, len(bitstream_data), 'bitstream'))
        
        # Update manifest for PSRAM regions
        updated_manifest = json.loads(json.dumps(manifest))  # Deep copy
        
        for region_info in updated_manifest.get("regions", []):
            if "filename" not in region_info:
                continue
                
            if region_info.get("psram_dst") is not None:
                if region_info.get("spiflash_src") is not None:
                    raise ValueError("Both psram_dst and spiflash_src set")
                    
                region_info["spiflash_src"] = firmware_base
                
                region_data = files.get(region_info["filename"])
                if region_data:
                    self.operations.append(FlashOperation(
                        filename=region_info["filename"],
                        offset=firmware_base,
                        file_type="raw",
                        data=region_data
                    ))
                    
                    self.regions.append(Region(
                        firmware_base,
                        region_info["size"],
                        region_info['filename']
                    ))
                
                # Align firmware base to next 4KB boundary
                firmware_base += region_info["size"]
                firmware_base = (firmware_base + 0xFFF) & ~0xFFF
        
        # Add manifest operation
        manifest_data = json.dumps(updated_manifest).encode('utf-8')
        # Pad manifest to MANIFEST_SIZE
        if len(manifest_data) > MANIFEST_SIZE:
            raise ValueError(f"Manifest too large: {len(manifest_data)} > {MANIFEST_SIZE}")
        manifest_data = manifest_data.ljust(MANIFEST_SIZE, b'\xff')
        
        self.operations.append(FlashOperation(
            filename="manifest.json",
            offset=manifest_addr,
            file_type="raw",
            data=manifest_data
        ))
        
        self.regions.append(Region(manifest_addr, MANIFEST_SIZE, 'manifest'))
        
        return updated_manifest
    
    def finalize_operations(self) -> List[FlashOperation]:
        """Finalize operations by setting skip_reset on all but the last."""
        if len(self.operations) > 1:
            for op in self.operations[:-1]:
                op.skip_reset = True
            self.operations[-1].skip_reset = False
        elif len(self.operations) == 1:
            self.operations[0].skip_reset = False
        
        return self.operations
    
    def process_archive(self, manifest: Dict, files: Dict[str, bytes], slot: Optional[int] = None) -> Tuple[List[FlashOperation], List[Region], Dict]:
        """
        Process an archive and prepare flash operations.
        
        Returns:
            Tuple of (operations, regions, updated_manifest)
        """
        self.manifest = manifest
        
        # Check XIP firmware
        has_xip, xip_offset = self.check_xip_firmware(manifest)
        
        # Validate slot assignment
        valid, error = self.validate_slot_assignment(has_xip, slot, xip_offset)
        if not valid:
            raise ValueError(error)
        
        # Prepare operations based on firmware type
        if has_xip:
            self.prepare_xip_firmware(manifest, files)
            updated_manifest = manifest
        else:
            updated_manifest = self.prepare_psram_firmware(manifest, files, slot)
        
        # Check for overlaps
        has_overlap, error = self.check_region_overlaps(self.regions, slot)
        if has_overlap:
            raise ValueError(error)
        
        # Finalize operations
        self.finalize_operations()
        
        return self.operations, self.regions, updated_manifest


def parse_manifest_from_flash(data: bytes) -> Optional[Dict]:
    """Parse JSON manifest from flash data."""
    try:
        # Find the end of the JSON data (null terminator or 0xFF)
        for delimiter in [b'\x00', b'\xff']:
            end_idx = data.find(delimiter)
            if end_idx != -1:
                break
        else:
            end_idx = len(data)

        json_bytes = data[:end_idx]
        return json.loads(json_bytes)
    except json.JSONDecodeError:
        return None


def is_empty_flash(data: bytes) -> bool:
    """Check if a flash segment is empty (all 0xFF)."""
    return all(b == 0xFF for b in data)
