import json
from typing import Any, Dict, Optional


def push(
    data: Dict[str, Any],
    bucket: str,
    key: str,
    profile: Optional[str] = None,
) -> None:
    """Upload data JSON to an S3 object."""
    try:
        import boto3
    except ImportError:
        raise ImportError("boto3 is required. Run: pip install \"promptvc[s3]\"")

    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    s3 = session.client("s3")
    body = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
    s3.put_object(Bucket=bucket, Key=key, Body=body, ContentType="application/json")


def pull(
    bucket: str,
    key: str,
    profile: Optional[str] = None,
) -> Dict[str, Any]:
    """Download and parse a JSON object from S3."""
    try:
        import boto3
    except ImportError:
        raise ImportError("boto3 is required. Run: pip install \"promptvc[s3]\"")

    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    s3 = session.client("s3")
    obj = s3.get_object(Bucket=bucket, Key=key)
    return json.loads(obj["Body"].read().decode("utf-8"))
