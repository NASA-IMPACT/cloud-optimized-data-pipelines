from cmr import CollectionQuery, GranuleQuery
import json
import boto3

batch_client = boto3.client("batch")

def get_link(granule, link_title):
    hrefs = [link["href"] for link in granule["links"]]
    if link_title:
        titles = [link["title"] if "title" in link else None for link in granule["links"]]
        href_index = titles.index(link_title)
    else:
        href_index = 0
    return hrefs[href_index]

def submit_job(event, file_url):
    response = batch_client.submit_job(
        jobName=event["job_name"],
        jobQueue=event["job_queue"],
        jobDefinition=event["job_def"],
        containerOverrides={
            "command": [
                "python",
                "run.py",
                "-c",
                event["collection_short_name"],
                "-f",
                file_url
            ]
        }     
    )
    return response

def lambda_handler(event, context):
    collection_short_name = event["collection_short_name"]
    link_title = event["link_title"]
    cmr_host = event.get("cmr_host")
    date_from = event.get("query").get("date_from")
    date_to = event.get("query").get("date_to")
    api = GranuleQuery()
    apiQuery = api.short_name(collection_short_name)
    if date_from and date_to:
      apiQuery = apiQuery.temporal(
          date_from=date_from,
          date_to=date_to)

    granules = apiQuery.get(20)
    statuses = []
    for granule in granules:
        file_url = get_link(granule, link_title)
        # statuses.append(file_url)
        response = submit_job(event, file_url)
        statuses.append(response["ResponseMetadata"]["HTTPStatusCode"])
    return statuses


event = {
    "collection_short_name": "GPM_3IMERGDF",
    "link_title": None,
    "job_name": "imerg-conversion-lambda",
    "job_queue": "default-job-queue",
    "job_def": "hdf5_to_cog_batch_job_def:5",
    "query": {
        "date_from": "2000-06-21T00:00:00Z",
        #"date_to": "2000-07-10T00:00:00Z"
    }
}
print(lambda_handler(event = event, context={}))
