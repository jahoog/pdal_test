#!/usr/bin/env python3
"""
LAS to COPC Converter
Converts LAS files to Cloud Optimized Point Cloud (COPC) format using PDAL
This uses a subprocess that calls the pdal executable directly
It checks that the pdal executable is installed
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_pdal():
    """Check if PDAL is installed"""
    try:
        result = subprocess.run(['pdal', '--version'], capture_output=True, text=True)
        print(f"PDAL version: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("ERROR: PDAL not found. Please install PDAL first.")
        print("Install with: brew install pdal  # on macOS")
        return False

def convert_las_to_copc(input_file, output_file=None):
    """Convert LAS file to COPC format"""
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"ERROR: Input file {input_file} not found")
        return False
    
    if not input_path.suffix.lower() in ['.las', '.laz']:
        print(f"ERROR: Input file must be .las or .laz format")
        return False
    
    # Generate output filename if not provided
    if output_file is None:
        output_file = input_path.with_suffix('.copc.laz')
    
    output_path = Path(output_file)
    
    print(f"Converting {input_path} to {output_path}")
    
    # PDAL pipeline for LAS to COPC conversion
    pipeline = {
        "pipeline": [
            str(input_path),
            {
                "type": "writers.copc",
                "filename": str(output_path),
                "forward": "all"
            }
        ]
    }
    
    # Write pipeline to temporary file
    pipeline_file = input_path.parent / "temp_pipeline.json"
    
    try:
        with open(pipeline_file, 'w') as f:
            json.dump(pipeline, f, indent=2)
        
        # Run PDAL pipeline
        cmd = ['pdal', 'pipeline', str(pipeline_file)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Successfully converted to {output_path}")
            print(f"Output file size: {output_path.stat().st_size / (1024*1024):.2f} MB")
            return True
        else:
            print(f"❌ Conversion failed:")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        return False
    
    finally:
        # Clean up temporary pipeline file
        if pipeline_file.exists():
            pipeline_file.unlink()

def main():
    if len(sys.argv) < 2:
        print("Usage: python las_to_copc_converter.py <input.las> [output.copc.laz]")
        print("Example: python las_to_copc_converter.py sample.las")
        sys.exit(1)
    
    if not check_pdal():
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = convert_las_to_copc(input_file, output_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
