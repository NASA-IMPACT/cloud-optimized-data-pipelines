#!/usr/bin/env python3
import os
from aws_cdk import core

from cdk.lambda_stack import LambdaStack
from cdk.step_function_stack import StepFunctionStack
from cdk.queue_stack import QueueStack

import config


app = core.App()

env_details = core.Environment(
    region=os.environ["CDK_DEFAULT_REGION"],
    account=os.environ["CDK_DEFAULT_ACCOUNT"],
)

lambda_stack = LambdaStack(
    app,
    f"{config.APP_NAME}-{config.ENV}-lambda",
    env=env_details,
)

queue_stack = QueueStack(
    app,
    f"{config.APP_NAME}-{config.ENV}-queue",
    lambda_stack,
    env=env_details,
)

step_function_stack = StepFunctionStack(
    app,
    f"{config.APP_NAME}-{config.ENV}-stepfunction",
    lambda_stack,
    queue_stack,
    env=env_details,
)

lambda_stack.grant_execution_privileges(
    lambda_function=lambda_stack.trigger_cogify_lambda,
    workflow=step_function_stack.cogify_workflow,
)
lambda_stack.grant_execution_privileges(
    lambda_function=lambda_stack.trigger_ingest_lambda,
    workflow=step_function_stack.publication_workflow,
)

app.synth()
