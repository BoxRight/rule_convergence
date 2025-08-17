#!/usr/bin/env python3
"""
Correct ZDD to CSV Converter
Uses the existing zdd_parser.py to properly parse ZDD files and generate analysis CSVs
"""

import sys
import csv
from pathlib import Path
from collections import defaultdict, Counter
from typing import List, Dict

# Import the existing parser
sys.path.insert(0, str(Path(__file__).parent.parent))
from zdd_parser import ZDDParser

class CorrectZDDAnalyzer:
    """Analyzes ZDD files using the correct parser"""
    
    def __init__(self):
        self.zdds: Dict[int, any] = {}
        self.thesis_mapping = {
            1: "2020418", 2: "2021246", 3: "2021398", 4: "2021537", 5: "2023487",
            6: "2025237", 7: "2025433", 8: "2029251", 9: "2030499", 10: "2030500", 11: "2030717"
        }
    
    def load_zdd_files(self, directory: Path) -> None:
        """Load all ZDD files using the correct parser"""
        zdd_files = sorted(directory.glob("zdd_*.bin"))
        
        if not zdd_files:
            raise FileNotFoundError(f"No ZDD binary files found in {directory}")
        
        print(f"Loading {len(zdd_files)} ZDD files with correct parser...")
        
        for zdd_file in zdd_files:
            # Extract ZDD number from filename
            zdd_num = int(zdd_file.stem.split('_')[1])
            
            parser = ZDDParser(zdd_file)
            structure = parser.load()
            self.zdds[zdd_num] = structure
            
            print(f"✓ Loaded {zdd_file.name}: magic={structure.magic_number}, arrays={len(structure.arrays)}")
    
    def generate_complete_csv(self, output_file: Path) -> None:
        """Generate complete CSV with all arrays and ZDD identification"""
        
        print(f"Generating complete CSV: {output_file}")
        
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                'zdd_id', 'thesis_number', 'magic_number', 'array_index', 
                'array_length', 'array_elements', 'array_signature_sorted',
                'element_position', 'element_value'
            ])
            
            total_arrays = 0
            total_elements = 0
            
            # Process each ZDD
            for zdd_id in sorted(self.zdds.keys()):
                structure = self.zdds[zdd_id]
                thesis_number = self.thesis_mapping.get(zdd_id, f"unknown_{zdd_id}")
                
                # Process each array in this ZDD
                for array_idx, array in enumerate(structure.arrays):
                    array_length = len(array)
                    array_elements = f"[{','.join(map(str, array))}]"
                    array_signature_sorted = f"[{','.join(map(str, sorted(array)))}]"
                    
                    # Write one row per element in the array
                    for element_pos, element_value in enumerate(array):
                        writer.writerow([
                            zdd_id, thesis_number, structure.magic_number, array_idx,
                            array_length, array_elements, array_signature_sorted,
                            element_pos, element_value
                        ])
                        total_elements += 1
                    
                    total_arrays += 1
        
        print(f"✓ Exported {total_arrays} arrays with {total_elements} total elements")
    
    def generate_array_summary_csv(self, output_file: Path) -> None:
        """Generate array-level summary (one row per array)"""
        
        print(f"Generating array summary CSV: {output_file}")
        
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                'zdd_id', 'thesis_number', 'magic_number', 'array_index', 
                'array_length', 'array_elements', 'array_signature_sorted',
                'unique_elements', 'min_element', 'max_element'
            ])
            
            # Process each ZDD
            for zdd_id in sorted(self.zdds.keys()):
                structure = self.zdds[zdd_id]
                thesis_number = self.thesis_mapping.get(zdd_id, f"unknown_{zdd_id}")
                
                # Process each array in this ZDD
                for array_idx, array in enumerate(structure.arrays):
                    array_length = len(array)
                    array_elements = f"[{','.join(map(str, array))}]"
                    array_signature_sorted = f"[{','.join(map(str, sorted(array)))}]"
                    unique_elements = len(set(array))
                    min_element = min(array) if array else 0
                    max_element = max(array) if array else 0
                    
                    writer.writerow([
                        zdd_id, thesis_number, structure.magic_number, array_idx,
                        array_length, array_elements, array_signature_sorted,
                        unique_elements, min_element, max_element
                    ])
        
        print(f"✓ Exported array summary")
    
    def generate_pattern_analysis_csv(self, output_file: Path) -> None:
        """Generate cross-ZDD pattern analysis"""
        
        print(f"Generating pattern analysis CSV: {output_file}")
        
        # Collect all array patterns
        pattern_occurrences = defaultdict(list)  # pattern -> [(zdd_id, array_index)]
        
        for zdd_id, structure in self.zdds.items():
            for array_idx, array in enumerate(structure.arrays):
                # Create canonical pattern (sorted for consistency)
                pattern = tuple(sorted(array))
                pattern_occurrences[pattern].append((zdd_id, array_idx))
        
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'array_signature', 'frequency_across_zdds', 'zdd_occurrences',
                'first_seen_zdd', 'array_length', 'unique_elements'
            ])
            
            for pattern, occurrences in sorted(pattern_occurrences.items(), 
                                             key=lambda x: len(x[1]), reverse=True):
                zdd_ids = [occ[0] for occ in occurrences]
                unique_zdds = sorted(set(zdd_ids))
                
                array_signature = f"[{','.join(map(str, pattern))}]"
                frequency = len(occurrences)
                zdd_occurrences = ','.join(map(str, unique_zdds))
                first_seen = min(unique_zdds)
                array_length = len(pattern)
                unique_elements = len(set(pattern))
                
                writer.writerow([
                    array_signature, frequency, zdd_occurrences,
                    first_seen, array_length, unique_elements
                ])
        
        print(f"✓ Generated pattern analysis")
    
    def print_summary(self) -> None:
        """Print analysis summary"""
        print("\n" + "="*60)
        print("CORRECT ZDD ANALYSIS SUMMARY")
        print("="*60)
        
        total_arrays = sum(len(structure.arrays) for structure in self.zdds.values())
        total_elements = sum(sum(len(array) for array in structure.arrays) for structure in self.zdds.values())
        
        # Collect all unique variables
        all_variables = set()
        for structure in self.zdds.values():
            for array in structure.arrays:
                all_variables.update(array)
        
        # Collect all unique array patterns
        all_patterns = set()
        for structure in self.zdds.values():
            for array in structure.arrays:
                all_patterns.add(tuple(sorted(array)))
        
        print(f"Total ZDDs analyzed: {len(self.zdds)}")
        print(f"Total arrays across all ZDDs: {total_arrays}")
        print(f"Total elements across all arrays: {total_elements}")
        print(f"Unique variables across all ZDDs: {len(all_variables)}")
        print(f"Unique array patterns: {len(all_patterns)}")
        print(f"Average arrays per ZDD: {total_arrays / len(self.zdds):.1f}")
        print(f"Average elements per array: {total_elements / total_arrays:.1f}")
        
        # Show variable range
        if all_variables:
            print(f"Variable ID range: {min(all_variables)} - {max(all_variables)}")
        
        # Show per-ZDD breakdown
        print(f"\nPer-ZDD Breakdown:")
        for zdd_id in sorted(self.zdds.keys()):
            structure = self.zdds[zdd_id]
            thesis_number = self.thesis_mapping.get(zdd_id, f"unknown_{zdd_id}")
            arrays_count = len(structure.arrays)
            elements_count = sum(len(array) for array in structure.arrays)
            print(f"  ZDD {zdd_id} (Thesis {thesis_number}): {arrays_count} arrays, {elements_count} elements")

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python zdd_to_csv_correct.py <directory_with_zdd_files>")
        print("Example: python zdd_to_csv_correct.py .")
        sys.exit(1)
    
    directory = Path(sys.argv[1])
    if not directory.exists():
        print(f"Error: Directory {directory} does not exist")
        sys.exit(1)
    
    try:
        # Initialize analyzer
        analyzer = CorrectZDDAnalyzer()
        
        # Load ZDD files
        analyzer.load_zdd_files(directory)
        
        # Create output directory
        output_dir = directory / "analysis" / "zdd_correct_analysis"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate all CSV files
        analyzer.generate_complete_csv(output_dir / "all_arrays_complete_correct.csv")
        analyzer.generate_array_summary_csv(output_dir / "arrays_summary_correct.csv")
        analyzer.generate_pattern_analysis_csv(output_dir / "pattern_analysis_correct.csv")
        
        # Print summary
        analyzer.print_summary()
        
        print(f"\n🎯 Correct analysis complete! Check {output_dir} for CSV files.")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 