#!/usr/bin/env python3
"""
ZDD Binary to Text Converter

Converts binary ZDD files (.bin) into text format that zdd_query.py expects.
The text format is arrays of integers like [1,2,3,4] on each line.
"""

import sys
from pathlib import Path
from typing import List, Optional
import logging

# Add src/python to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from zdd_parser import ZDDParser

logger = logging.getLogger(__name__)


class ZDDBinaryToTextConverter:
    """Converts binary ZDD files to text format for zdd_query.py"""
    
    def __init__(self):
        self.parser = None
        
    def convert_binary_to_text(self, binary_file: Path, output_file: Optional[Path] = None) -> Path:
        """Convert a single binary ZDD file to text format"""
        
        if not binary_file.exists():
            raise FileNotFoundError(f"Binary ZDD file not found: {binary_file}")
            
        logger.info(f"Converting {binary_file.name} to text format")
        
        # Parse the binary file
        parser = ZDDParser(binary_file)
        structure = parser.load()
        
        # Determine output file
        if output_file is None:
            output_file = binary_file.with_suffix('.txt')
        
        # Convert arrays to text format
        self._write_arrays_to_text(structure.arrays, output_file)
        
        logger.info(f"Converted to: {output_file}")
        return output_file
    
    def convert_multiple_binary_files(self, binary_files: List[Path], output_file: Optional[Path] = None) -> Path:
        """Convert multiple binary ZDD files and output each ZDD's arrays separately"""
        
        if not binary_files:
            raise ValueError("No binary ZDD files provided")
        
        logger.info(f"Converting {len(binary_files)} binary ZDD files")
        
        # Determine output file
        if output_file is None:
            output_file = binary_files[0].parent / "zdd_vectors.txt"
        
        # Write each ZDD's arrays separately
        with open(output_file, 'w') as f:
            for i, binary_file in enumerate(binary_files):
                if not binary_file.exists():
                    logger.warning(f"File not found: {binary_file}")
                    continue
                    
                parser = ZDDParser(binary_file)
                structure = parser.load()
                
                # Write ZDD separator and metadata
                f.write(f"# ZDD {i+1}: {binary_file.name}\n")
                f.write(f"# Magic: {structure.magic_number}\n")
                f.write(f"# Arrays: {len(structure.arrays)}\n")
                f.write(f"#\n")
                
                # Write each array from this ZDD on its own line
                for array in structure.arrays:
                    array_text = f"[{','.join(map(str, array))}]"
                    f.write(array_text + "\n")
                
                # Add separator between ZDDs
                f.write(f"#\n")
                f.write(f"# End of ZDD {i+1}\n")
                f.write(f"#\n")
                
                logger.info(f"Added {len(structure.arrays)} arrays from {binary_file.name}")
        
        logger.info(f"Converted {len(binary_files)} files to: {output_file}")
        return output_file
    
    def _write_arrays_to_text(self, arrays: List[List[int]], output_file: Path) -> None:
        """Write arrays to text file in the format zdd_query.py expects"""
        
        with open(output_file, 'w') as f:
            for array in arrays:
                # Convert array to text format: [1,2,3,4]
                array_text = f"[{','.join(map(str, array))}]"
                f.write(array_text + '\n')
        
        logger.info(f"Wrote {len(arrays)} arrays to {output_file}")
    
    def print_conversion_summary(self, arrays: List[List[int]], source_file: str) -> None:
        """Print a summary of the converted data"""
        
        print(f"\n📊 Conversion Summary: {source_file}")
        print("=" * 50)
        print(f"Total Arrays: {len(arrays)}")
        
        if arrays:
            total_elements = sum(len(array) for array in arrays)
            avg_length = total_elements / len(arrays)
            min_length = min(len(array) for array in arrays)
            max_length = max(len(array) for array in arrays)
            
            print(f"Total Elements: {total_elements}")
            print(f"Average Array Length: {avg_length:.1f}")
            print(f"Array Length Range: {min_length} - {max_length}")
            
            # Show unique integers
            all_integers = set()
            for array in arrays:
                all_integers.update(array)
            
            print(f"Unique Integers: {len(all_integers)}")
            if all_integers:
                print(f"Integer Range: {min(all_integers)} - {max(all_integers)}")
            
            # Show first few arrays
            print(f"\n📋 First 5 Arrays:")
            for i, array in enumerate(arrays[:5]):
                print(f"  Array {i}: {array}")
            
            if len(arrays) > 5:
                print(f"  ... and {len(arrays) - 5} more arrays")
        
        print()


def convert_zdd_binary_file(binary_file: Path, output_file: Optional[Path] = None) -> Path:
    """Convenience function to convert a single binary ZDD file"""
    converter = ZDDBinaryToTextConverter()
    return converter.convert_binary_to_text(binary_file, output_file)


def convert_zdd_binary_directory(directory: Path, output_file: Optional[Path] = None) -> Path:
    """Convert all zdd*.bin files in a directory"""
    binary_files = list(directory.glob("zdd*.bin"))
    
    if not binary_files:
        raise FileNotFoundError(f"No zdd*.bin files found in {directory}")
    
    converter = ZDDBinaryToTextConverter()
    return converter.convert_multiple_binary_files(binary_files, output_file)


def convert_job_directory(job_dir: Path) -> tuple[Path, Path]:
    """Convert both witness_export files and ZDD binary files for a job directory"""
    
    job_dir = Path(job_dir)
    witness_output_dir = job_dir / "witness_output"
    
    if not witness_output_dir.exists():
        raise FileNotFoundError(f"Witness output directory not found: {witness_output_dir}")
    
    # Convert witness_export files to kelsen_data.json
    from witness_export_converter import convert_witness_export_directory
    kelsen_data_file = convert_witness_export_directory(witness_output_dir)
    
    # Convert ZDD binary files to text
    zdd_text_file = convert_zdd_binary_directory(witness_output_dir)
    
    return kelsen_data_file, zdd_text_file


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert binary ZDD files to text format")
    parser.add_argument("input", help="Binary ZDD file, directory, or job directory")
    parser.add_argument("-o", "--output", help="Output file (default: auto-generated)")
    parser.add_argument("--job", action="store_true", help="Treat input as job directory and convert both formats")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else None
    
    try:
        if args.job:
            # Convert job directory (both formats)
            kelsen_file, zdd_file = convert_job_directory(input_path)
            print(f"✅ Converted job directory:")
            print(f"  kelsen_data.json: {kelsen_file}")
            print(f"  zdd_vectors.txt: {zdd_file}")
        elif input_path.is_file():
            # Convert single binary file
            result = convert_zdd_binary_file(input_path, output_path)
            print(f"✅ Converted: {result}")
        elif input_path.is_dir():
            # Convert directory of binary files
            result = convert_zdd_binary_directory(input_path, output_path)
            print(f"✅ Converted directory: {result}")
        else:
            print(f"❌ Error: {input_path} is not a file or directory")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1) 