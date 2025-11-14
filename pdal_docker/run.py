import pdal
import json
import os
import sys
import boto3
from pathlib import Path

s3_client = boto3.client("s3")
S3_TARGET_FOLDER = os.environ['S3_TARGET_FOLDER']
S3_TARGET_BUCKET = os.environ['S3_TARGET_BUCKET']
S3_SOURCE_FOLDER = os.environ['S3_SOURCE_FOLDER']
S3_SOURCE_BUCKET = os.environ['S3_SOURCE_BUCKET']

def get_s3_files(source_bucket, source_folder):
    response = s3_client.list_objects_v2(
        Bucket=source_bucket,
        Prefix=source_folder
    )
    return response

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

    try:
        json_pipeline = json.dumps(pipeline)
        pipe = pdal.Pipeline(json_pipeline)
        count = pipe.execute()
        metadata = pipe.metadata
        print(f"Processed {count} points. COPC output: {output_path}")
        print(f"Output file size: {output_path.stat().st_size / (1024*1024):.2f} MB")
        return True
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        return False
    finally:
        # Clean up temporary pipeline file
        print("Done")

print(pdal.__version__);

s3_resp = get_s3_files(S3_SOURCE_BUCKET, S3_SOURCE_FOLDER)

file_count = 0
for file in s3_resp['Contents']:
    if (file['Key'] != S3_SOURCE_FOLDER):
        file_count = file_count + 1
        print(file['Key'])
        s3_key = file['Key']
        filename = os.path.basename(s3_key)
        s3_client.download_file(S3_SOURCE_BUCKET, file['Key'], filename)
        input_file = filename
        output_file = filename + ".copc"
        success = convert_las_to_copc(input_file, output_file)
        response = s3_client.upload_file(output_file, S3_TARGET_BUCKET, S3_TARGET_FOLDER + output_file)
        os.remove(output_file)
        os.remove(input_file)

print("Completed conversions: ", file_count)
