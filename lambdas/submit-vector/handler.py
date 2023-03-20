import boto3
import requests
import os
import subprocess
import json
from urllib.parse import urlparse


def download_file(file_uri: str):
    sts = boto3.client("sts")
    response = sts.assume_role(
        RoleArn="arn:aws:iam::114506680961:role/veda-data-store-read-staging",
        RoleSessionName="sts-assume-114506680961",
    )
    new_session = boto3.Session(
        aws_access_key_id=response["Credentials"]["AccessKeyId"],
        aws_secret_access_key=response["Credentials"]["SecretAccessKey"],
        aws_session_token=response["Credentials"]["SessionToken"],
    )
    s3 = new_session.client("s3")

    url_parse = urlparse(file_uri)

    bucket = url_parse.netloc
    path = url_parse.path[1:]
    filename = url_parse.path.split("/")[-1]
    target_filepath = os.path.join("/tmp", filename)

    s3.download_file(bucket, path, target_filepath)

    print(f"downloaded {target_filepath}")

    sts.close()
    return target_filepath


def get_connection_string(secret: dict, as_uri: bool = False) -> str:
    if as_uri:
        return f"postgresql://{secret['username']}:{secret['password']}@{secret['host']}:5432/{secret['dbname']}"
    else:
        return f"PG:host={secret['host']} dbname={secret['dbname']} user={secret['username']} password={secret['password']}"


def get_secret(secret_name: str) -> None:
    """Retrieve secrets from AWS Secrets Manager

    Args:
        secret_name (str): name of aws secrets manager secret containing database connection secrets
        profile_name (str, optional): optional name of aws profile for use in debugger only

    Returns:
        secrets (dict): decrypted secrets in dict
    """

    # Create a Secrets Manager client
    session = boto3.session.Session(region_name="us-west-1")
    client = session.client(service_name="secretsmanager")

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    get_secret_value_response = client.get_secret_value(SecretId=secret_name)

    # Decrypts secret using the associated KMS key.
    # Depending on whether the secret is a string or binary, one of these fields will be populated.
    if "SecretString" in get_secret_value_response:
        return json.loads(get_secret_value_response["SecretString"])
    else:
        return json.loads(base64.b64decode(get_secret_value_response["SecretBinary"]))


def load_to_featuresdb(filename: str, collection: str):
    secret_name = os.environ.get("VECTOR_SECRET_NAME")

    con_secrets = get_secret(secret_name)
    connection = get_connection_string(con_secrets)

    print(f"running ogr2ogr import for collection: {collection}")

    if collection in ["fireline", "newfirepix"]:
        subprocess.run(
            [
                "ogr2ogr",
                "-f",
                "PostgreSQL",
                connection,
                "-t_srs",
                "EPSG:4326",
                filename,
                "-nln",
                f"eis_fire_{collection}",
                "-overwrite",
                "-progress",
            ]
        )
    elif collection == "perimeter":
        subprocess.run(
            [
                "ogr2ogr",
                "-f",
                "PostgreSQL",
                connection,
                "-t_srs",
                "EPSG:4326",
                filename,
                "-nln",
                f"eis_fire_{collection}",
                "-overwrite",
                "-sql",
                "SELECT n_pixels, n_newpixels, farea, fperim, flinelen, duration, pixden, meanFRP, isactive, t_ed as t, fireID from perimeter",
                "-progress",
            ]
        )


def alter_datetime_add_indexes(filename: str, collection: str):
    secret_name = os.environ.get("VECTOR_SECRET_NAME")

    con_secrets = get_secret(secret_name)
    connection = get_connection_string(secret=con_secrets, as_uri=True)

    subprocess.run(
        [
            "psql",
            connection,
            "-c",
            f"ALTER table eis_fire_{collection} ALTER COLUMN t TYPE TIMESTAMP without time zone;CREATE INDEX IF NOT EXISTS idx_eis_fire_{collection}_datetime ON eis_fire_{collection}(t);",
        ]
    )


def handler(event, context):
    href = event["s3_filename"]
    collection = event["collection"]

    downloaded_filepath = download_file(href)

    print(f"[ DOWNLOAD FILEPATH ]: {downloaded_filepath}")
    print(f"[ COLLECTION ]: {collection}")
    load_to_featuresdb(downloaded_filepath, collection)
    alter_datetime_add_indexes(downloaded_filepath, collection)

    # this is annoying, tipg needs to refresh the catalog after an `overwrite`
    resp = requests.get(url="https://firenrt.delta-backend.com/refresh")
    print(f"[ REFRESH STATUS CODE ]: {resp.status_code}")
    print(f"[ REFRESH JSON ]: {resp.json()}")


if __name__ == "__main__":
    sample_event = {
        "collection": "eis_fire_newfirepix_2",
        "href": "s3://covid-eo-data/fireline/newfirepix.fgb",
    }
    handler(sample_event, {})
