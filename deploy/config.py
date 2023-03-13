from getpass import getuser

from pydantic import BaseSettings, Field

class Config(BaseSettings):
    owner: str = Field(
        description=" ".join(
            [
                "Name of primary contact for Cloudformation Stack.",
                "Used to tag generated resources",
                "Defaults to current username.",
            ]
        ),
        default_factory=getuser,
    )

    ENV: str = Field(
        Description="Environment name (defaults to current username)",
        env='ENV',
        default_factory=getuser
    )

    COGNITO_APP_SECRET: str = Field(
        Description="Cognito app secret",
        env='COGNITO_APP_SECRET',
    )
    STAC_INGESTOR_URL: str = Field(
        Description="URL of STAC Ingestor",
        env='STAC_INGESTOR_URL',
    )

    EARTHDATA_USERNAME: str = Field(
        Description="Earthdata username",
        env='EARTHDATA_USERNAME',
        default="XXXX"
    )
    EARTHDATA_PASSWORD: str = Field(
        Description="Earthdata password",
        env='EARTHDATA_PASSWORD',
        default="XXXX"
    )

    APP_NAME: str = "veda-data-pipelines"
    VEDA_DATA_BUCKET: str = "climatedashboard-data"
    VEDA_EXTERNAL_BUCKETS = ["nasa-maap-data-store", "covid-eo-blackmarble"]
    MCP_BUCKETS = {
        "prod": "veda-data-store",
        "stage": "veda-data-store-staging",
    }

    # This should throw if it is not provided
    EXTERNAL_ROLE_ARN: str = Field(
        Description="ARN of role to assume for external buckets",
        env='EXTERNAL_ROLE_ARN',
    )
