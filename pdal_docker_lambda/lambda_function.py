
import pdal
import json
import os
import sys
import subprocess
import boto3
from pathlib import Path

s3_client = boto3.client("s3")
S3_TARGET_FOLDER = os.environ['S3_TARGET_FOLDER']
S3_TARGET_BUCKET = os.environ['S3_TARGET_BUCKET']
TEMP_FILE_LOCATION = "/tmp"

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


def handler(event, context):
    S3_SOURCE_BUCKET=event['S3_SOURCE_BUCKET']
    S3_SOURCE_OBJECT=event['S3_SOURCE_OBJECT']

    filename = os.path.basename(S3_SOURCE_OBJECT)
    s3_client.download_file(S3_SOURCE_BUCKET, S3_SOURCE_OBJECT, TEMP_FILE_LOCATION + "/" + filename)
    input_file = filename
    output_file = filename + ".copc"
    success = convert_las_to_copc(TEMP_FILE_LOCATION + "/" + input_file, TEMP_FILE_LOCATION + "/" + output_file)

    response = s3_client.upload_file(TEMP_FILE_LOCATION + "/" + output_file, S3_TARGET_BUCKET, S3_TARGET_FOLDER + output_file)
    os.remove(output_file)
    os.remove(input_file)


    return {
            "PDAL VERSION": pdal.__version__,
            "SYS VERSION": sys.version,
            "S3 SOURCE BUCKET": S3_SOURCE_BUCKET,
            "S3 SOURCE OBJECT": S3_SOURCE_OBJECT,
            "CONVERSION": success,
    }
