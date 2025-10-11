import re
import os
import tempfile
import subprocess
from typing import Optional
from colorama import Fore, Style

from ..build.types import RegionType

TILIQUA_OPENFPGALOADER = os.getenv('TILIQUA_OPENFPGALOADER', 'openFPGALoader')
_CMD_BASE = [TILIQUA_OPENFPGALOADER, "-c", "dirtyJtag"]

class OpenFPGALoaderCommandSequence:

    """
    Generates the ``openFPGALoader`` commands needed in order
    to flash each region to the hardware.
    """

    def __init__(self):
        self._commands = []

    @staticmethod
    def from_flashable_regions(regions, erase_option_storage=False):
        sequence = OpenFPGALoaderCommandSequence()
        for region in regions:
            if region.memory_region.region_type == RegionType.OptionStorage:
                if erase_option_storage:
                    sequence = sequence.with_erase_cmd(region.addr, region.memory_region.size)
                continue
            sequence = sequence.with_flash_cmd(str(region.memory_region.filename), region.addr, "raw")
        return sequence

    @staticmethod
    def _create_erased_file(size: int) -> str:
        """
        Create a temporary file filled with 0xff bytes (erased flash state).
        This is used to erase sectors because openFPGALoader does not have such a command.
        """
        import tempfile
        fd, path = tempfile.mkstemp(suffix=".erase.bin")
        try:
            with os.fdopen(fd, 'wb') as f:
                f.write(b'\xff' * size)
        except:
            os.close(fd)
            raise
        return path


    def with_flash_cmd(self, path: str, offset: int, file_type: str = "auto"):
        # Command to flash a file to a specific flash offset.
        # Add commands using a builder pattern:  o.with_flash_cmd(...).execute()
        cmd = _CMD_BASE + [
            "-f", "-o", f"{hex(offset)}",
        ]
        if file_type != "auto":
            cmd.extend(["--file-type", file_type])
        cmd.append(path)
        self._commands.append(cmd)
        return self

    def with_erase_cmd(self, offset: int, size: int):
        # Command to flash 0xff*size bytes to offset (same as erasing)
        temp_file = self._create_erased_file(size)
        return self.with_flash_cmd(temp_file, offset, "raw")

    @property
    def commands(self):
        commands = self._commands.copy()
        # Add skip-reset flag to all but the last command
        if len(commands) > 1:
            for cmd in commands[:-1]:
                if "--skip-reset" not in cmd:
                    cmd.insert(-1, "--skip-reset")
        return commands

    def execute(self, cwd=None):
        """
        Execute flashing commands on the hardware.

        ``cwd`` should normally be the path to which the bitstream
        archive was extracted, so ``openFPGALoader`` can find the files
        that it needs to flash.
        """
        print("\nExecuting commands...")
        for cmd in self.commands:
            subprocess.check_call(cmd, cwd=cwd)

def scan_for_tiliqua_hardware_version() -> Optional[int]:
    """
    Scan for a debugger with "apfbug" in the product name using openFPGALoader.
    Return the attached Tiliqua hardware version, or None if nothing found.
    """
    print("Scan for Tiliqua...")
    try:
        result = subprocess.run(
            [TILIQUA_OPENFPGALOADER, "--scan-usb"],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running {TILIQUA_OPENFPGALOADER}: {e}")
        sys.exit(1)
    print(f"{Fore.BLUE}{Style.BRIGHT}{output}{Style.RESET_ALL}")
    lines = output.strip().split('\n')
    for line in lines:
        if "apfbug" in line.lower() or "apf.audio" in line.lower():
            # Extract serial (16-char hex string) and product (contains "Tiliqua R#")
            serial_match = re.search(r'\b([A-F0-9]{16})\b', line)
            product_match = re.search(r'(Tiliqua\s+R\d+[^$]*)', line, re.IGNORECASE)
            if serial_match and product_match:
                serial = serial_match.group(1)
                product = product_match.group(1).strip()
                hw_version_match = re.search(r'R(\d+)', product)
                if hw_version_match:
                    hw_version = int(hw_version_match.group(1))
                    print(f"Found Tiliqua! (hw_rev={Style.BRIGHT}{hw_version}{Style.RESET_ALL}, serial={Style.BRIGHT}{serial}{Style.RESET_ALL})")
                    return hw_version
                else:
                    print("Found tiliqua-like device, product code is malformed (update RP2040?).")
    return None

def dump_flash_region(offset: int, size: int, reset: bool = False) -> bytes:
    # Create a unique filename, for use by openFPGALoader
    with tempfile.NamedTemporaryFile(suffix='.bin', delete=True) as tmp_file:
        temp_file_name = tmp_file.name
    # Dump the spiflash region to this temporary filename
    # FIXME: dumping to stdout and capturing it does not work somehow.
    cmd = _CMD_BASE + [
        "--dump-flash", "-o", f"{hex(offset)}",
        "--file-size", str(size),
    ]
    if not reset:
        # Spamming the FPGA with resets is not nice for audio pops.
        cmd.append("--skip-reset")
    cmd.append(temp_file_name)
    print(" ".join(cmd)) # command we are running
    subprocess.check_call(cmd)
    # Finally, read out the contents and return them.
    with open(temp_file_name, 'rb') as f:
        return f.read()

