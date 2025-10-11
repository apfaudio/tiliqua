import copy

from ..build.types import *

class SlotLayout:

    """
    Given a slot number e.g. ``SlotLayout(None)`` (bootloader) or ``SlotLayout(3)``
    (for user bitstreams), provide a bunch of methods to query desired SPI flash
    layout.

    This is used by ``compute_concrete_regions_to_flash`` to determine which flash
    addresses to load e.g. bitstreams or firmware, and to update the same value in
    the manifest flashed to the device.
    """

    BOOTLOADER_BITSTREAM_ADDR = 0x00000
    FIRMWARE_BASE_OFFSET = 0x90000
    OPTIONS_BASE_OFFSET = 0xE0000

    def __init__(self, slot_number: Optional[int] = None):
        self.slot_number = slot_number  # None = bootloader, int = user slot

    @property
    def is_bootloader(self) -> bool:
        return self.slot_number is None

    @property
    def bitstream_addr(self) -> int:
        if self.is_bootloader:
            return self.BOOTLOADER_BITSTREAM_ADDR
        else:
            return SLOT_BITSTREAM_BASE + (self.slot_number * SLOT_SIZE)

    @property
    def manifest_addr(self) -> int:
        if self.is_bootloader:
            return MANIFEST_OFFSET
        else:
            return self.bitstream_addr + MANIFEST_OFFSET

    @property
    def firmware_base(self) -> int:
        if self.is_bootloader:
            raise ValueError("Bootloader doesn't have firmware base (uses XiP)")
        return self.FIRMWARE_BASE_OFFSET + ((1+self.slot_number) * SLOT_SIZE)

    @property
    def options_base(self) -> int:
        if self.is_bootloader:
            return self.OPTIONS_BASE_OFFSET
        else:
            return self.OPTIONS_BASE_OFFSET + ((1+self.slot_number) * SLOT_SIZE)

    @property
    def slot_start_addr(self) -> int:
        return self.bitstream_addr

    @property
    def slot_end_addr(self) -> int:
        return self.bitstream_addr + SLOT_SIZE


class FlashableRegion:

    """Wrapper for a ``MemoryRegion`` that has an assigned (final) SPIflash address."""

    def __init__(self, memory_region):
        self.memory_region = memory_region

    @property
    def addr(self) -> int:
        """Address where this region will be written to SPI flash."""
        return self.memory_region.spiflash_src

    @property
    def size(self) -> int:
        return self.memory_region.size

    @property
    def aligned_size(self) -> int:
        """Return size aligned up to sector boundary."""
        return (self.size + FLASH_SECTOR_SZ - 1) & ~(FLASH_SECTOR_SZ - 1)

    @property
    def end_addr(self) -> int:
        # End address (exclusive).
        return self.addr + self.aligned_size

    def __lt__(self, other):
        # Used for sorting regions by address for overlap detection.
        return self.addr < other.addr

    def __str__(self) -> str:
        result = (f"{self.memory_region.filename} ({self.memory_region.region_type}):\n"
                  f"    start: 0x{self.addr:x}\n"
                  f"    end:   0x{self.addr + self.aligned_size - 1:x}")
        return result


def compute_concrete_regions_to_flash(
    manifest: BitstreamManifest, slot: Optional[int]) -> (BitstreamManifest, List[FlashableRegion]):

    """
    Given a manifest, walk all the regions in it, assigning real SPI flash addresses
    to any regions that need them depending on the current slot assignment.

    After assignment, check the addresses for any overlap our out-of-slot conditions.

    Returns an updated manifest and list of FlashableRegion.

    The updated manifest (with concrete spi flash addresses) should be the one
    written to the flash, so the SoC knows where to find things.
    """

    manifest = copy.deepcopy(manifest)
    layout = SlotLayout(slot)
    regions_to_flash = []

    ramload_base = None
    if not layout.is_bootloader:
        ramload_base = layout.firmware_base

    # Update all regions with real SPIflash addresses, where needed.
    for region in manifest.regions:
        match region.region_type:
            case RegionType.Bitstream:
                region.spiflash_src = layout.bitstream_addr
            case RegionType.Manifest:
                region.spiflash_src = layout.manifest_addr
            case RegionType.XipFirmware:
                # XipFirmware regions already have spiflash_src set from archive creation
                assert region.spiflash_src is not None, "XipFirmware region missing spiflash_src"
            case RegionType.OptionStorage:
                region.spiflash_src = layout.options_base
            case RegionType.RamLoad:
                assert region.spiflash_src is None, "RamLoad region already has spiflash_src set"
                region.spiflash_src = ramload_base
                print(f"manifest: region {region.filename}: spiflash_src set to 0x{ramload_base:x}")
                # Align firmware base to next flash sector boundary
                ramload_base += region.size
                ramload_base = (ramload_base + FLASH_SECTOR_SZ - 1) & ~(FLASH_SECTOR_SZ - 1)

    # Create a list of regions that exist in the SPI flash (not virtual regions)
    for region in manifest.regions:
        if region.spiflash_src is not None:
            regions_to_flash.append(FlashableRegion(region))

    # Check for any overlapping regions

    # For non-XIP firmware, check if any region exceeds its slot
    for region in regions_to_flash:
        if region.end_addr > layout.slot_end_addr:
            raise ValueError(f"Region {region.name} exceeds slot boundary: "
                             f"ends at 0x{region.end_addr:x}, slot ends at 0x{layout.slot_end_addr:x}")

    # Sort by start address and check for overlaps
    sorted_regions = sorted(regions_to_flash)
    for i in range(len(sorted_regions) - 1):
        curr_end = sorted_regions[i].end_addr
        next_start = sorted_regions[i + 1].addr
        if curr_end > next_start:
            raise ValueError(f"Overlap detected between {sorted_regions[i].name} (ends at 0x{curr_end:x}) "
                             f"and {sorted_regions[i+1].name} (starts at 0x{next_start:x})")

    return (manifest, regions_to_flash)
