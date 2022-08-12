import os


# VPC that contains the target database to which STAC records will be inserted
VPC_ID = os.environ.get("VPC_ID")
SECURITY_GROUP_ID = os.environ.get("SECURITY_GROUP_ID")
ENV = os.environ.get("ENV")
SECRET_NAME = os.environ.get("SECRET_NAME")
EARTHDATA_USERNAME = os.environ.get("EARTHDATA_USERNAME")
EARTHDATA_PASSWORD = os.environ.get("EARTHDATA_PASSWORD")

APP_NAME = os.environ.get("APP_NAME") or "delta-simple-ingest"
VEDA_DATA_BUCKET = "climatedashboard-data"
VEDA_EXTERNAL_BUCKETS = ["nasa-maap-data-store", "covid-eo-blackmarble"]
MCP_BUCKETS = {
    "prod": "veda-data-store",
    "stage": "veda-data-store-staging",
}

MCP_ROLE_ARN = os.environ.get("MCP_ROLE_ARN")
