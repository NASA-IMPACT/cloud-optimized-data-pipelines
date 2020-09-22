data "external" "ssm_data" {
  program = ["bash", "generate-ssm.sh", "/cloud-optimized-dp/", "SecureString"]
}

resource "aws_batch_job_definition" "hdf5_to_cog_batch_job_def" {
  name = "hdf5_to_cog_batch_job_def"
  type = "container"

  container_properties = <<CONTAINER_PROPERTIES
{
    "command": ["./run.py"],
    "image": "${data.aws_caller_identity.current.account_id}.dkr.ecr.${data.aws_region.current.name}.amazonaws.com/hdf5-to-cog:latest",
    "memory": 2048,
    "vcpus": 2,
    "secrets": ${data.external.ssm_data.result["ENVS"]},
    "logConfiguration": {
      "logDriver": "awslogs",
      "secretOptions": null,
      "options": {
        "awslogs-group": "/batch/hdf5-to-cog",
        "awslogs-region": "${data.aws_region.current.name}",
        "awslogs-stream-prefix": "batch"
      }
    }
}
CONTAINER_PROPERTIES
}