import boto3
from botocore.exceptions import ClientError

bucket_name = "abinaya-portfolio-site-demo-june"
region = "ap-south-1"

s3 = boto3.resource('s3', region_name=region)
client = boto3.client('s3', region_name=region)

try:
    bucket = s3.Bucket(bucket_name)

    print(f"🗑 Deleting all objects in bucket: {bucket_name}")

    # Delete all objects
    bucket.objects.all().delete()

    print("✔ All objects deleted.")

    # Delete bucket policy
    try:
        client.delete_bucket_policy(Bucket=bucket_name)
        print("✔ Bucket policy removed.")
    except:
        print("⚠ No bucket policy to delete.")

    # Delete website config
    try:
        client.delete_bucket_website(Bucket=bucket_name)
        print("✔ Website hosting removed.")
    except:
        print("⚠ No website config found.")

    # Delete the bucket itself
    bucket.delete()
    print(f"🎉 Bucket '{bucket_name}' deleted successfully!")

except ClientError as e:
    print(f"❌ Error: {e}")
