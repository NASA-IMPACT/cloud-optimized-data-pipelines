# Script to populate the environment variables for CDK deployment/pgstac database ingestion

# Usage: source env.sh <env>
# Valid environments: dev, stage (for now)

devPGSecret=xxxx
stagePGSecret=xxxx

devVPCid=vpc-xxxx
stageVPCid=vpc-xxxx

devSGid=sg-xxxx
stageSGid=sg-xxxx

if [[ -z $1 ]]
then
    echo "please provide an environment as the first argument"
else

    if [[ $1 = 'stage' ]]
    then
        pgSecret=$stagePGSecret
        vpcId=$stageVPCid
        sgId=$stageSGid
        export MCP_ROLE_ARN="arn:aws:iam::xxxxxx:role/xxxxx"
    else
        pgSecret=$devPGSecret
        vpcId=$devVPCid
        sgId=$devSGid
    fi

    export EARTHDATA_USERNAME=XXXX
    export EARTHDATA_PASSWORD=XXXX
    export VPC_ID=$vpcId
    export SECURITY_GROUP_ID=$sgId
    export SECRET_NAME=$pgSecret
    export ENV=$1
    export APP_NAME="delta-simple-ingest"

    echo "$1 environment set"
fi
