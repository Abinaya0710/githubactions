import boto3
from botocore.exceptions import ClientError
import os

# --- CONFIG ---
bucket_name = "abinaya-portfolio-site-demo"   # must be globally unique
region = "ap-south-1"
local_folder = r"site"  # folder with index.html + images
# ----------------

s3 = boto3.client('s3', region_name=region)

try:
    # 1️⃣ Create bucket
    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={'LocationConstraint': region}
    )
    print(f"✅ Bucket '{bucket_name}' created.")

    # 2️⃣ Disable Block Public Access
    s3.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': False,
            'IgnorePublicAcls': False,
            'BlockPublicPolicy': False,
            'RestrictPublicBuckets': False
        }
    )
    print("🔓 Disabled Block Public Access")

    # 3️⃣ Upload all files
    for root, dirs, files in os.walk(local_folder):
        for file in files:
            path_on_local = os.path.join(root, file)
            path_in_s3 = os.path.relpath(path_on_local, local_folder).replace("\\", "/")

            # Auto-detect content types
            if file.endswith(".html"):
                content_type = "text/html"
            elif file.endswith(".css"):
                content_type = "text/css"
            elif file.endswith(".js"):
                content_type = "application/javascript"
            elif file.endswith(".png"):
                content_type = "image/png"
            elif file.endswith(".jpg") or file.endswith(".jpeg"):
                content_type = "image/jpeg"
            else:
                content_type = "binary/octet-stream"

            s3.upload_file(
                path_on_local,
                bucket_name,
                path_in_s3,
                ExtraArgs={'ContentType': content_type}
            )

            print(f"📤 Uploaded: {path_in_s3} ({content_type})")

    # 4️⃣ Add bucket policy for public read
    policy_json = f"""{{
        "Version": "2012-10-17",
        "Statement": [
            {{
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::{bucket_name}/*"
            }}
        ]
    }}"""

    s3.put_bucket_policy(
        Bucket=bucket_name,
        Policy=policy_json
    )
    print("🌍 Public Read Enabled (Bucket Policy Added)")

    # 5️⃣ Enable static website hosting
    s3.put_bucket_website(
        Bucket=bucket_name,
        WebsiteConfiguration={
            'IndexDocument': {'Suffix': 'index.html'},
            'ErrorDocument': {'Key': 'index.html'}
        }
    )
    print("🌐 Static website hosting enabled!")

    print(f"\n✅ Site URL: http://{bucket_name}.s3-website.{region}.amazonaws.com")

except ClientError as e:
    print(f"❌ Error: {e}")
