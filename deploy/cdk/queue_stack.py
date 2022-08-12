from aws_cdk import (
    core,
    aws_sqs as sqs,
    aws_lambda_event_sources as lambda_event_sources,
)


class QueueStack(core.Stack):
    def __init__(self, app, construct_id, lambda_stack, **kwargs) -> None:
        super().__init__(app, construct_id, **kwargs)

        trigger_cogify_lambda = lambda_stack.lambdas["trigger_cogify_lambda"]
        trigger_ingest_lambda = lambda_stack.lambdas["trigger_ingest_lambda"]
        cogify_lambda = lambda_stack.lambdas["cogify_lambda"]

        self.cogify_queue = self._queue(
            f"{construct_id}-cogify-queue",
            visibility_timeout=900,
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=5,
                queue=self._queue(f"{construct_id}-cogify-dlq"),
            ),
        )

        trigger_cogify_lambda.add_event_source(
            lambda_event_sources.SqsEventSource(
                self.cogify_queue,
                batch_size=10,
                max_batching_window=core.Duration.seconds(20),
                report_batch_item_failures=True,
            )
        )

        self.stac_ready_queue = self._queue(
            f"{construct_id}-stac-ready-queue",
            # to resolve error
            # `Queue visibility timeout: 600 seconds is less than Function timeout: 900 seconds`
            visibility_timeout=900,
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=3,
                queue=self._queue(f"{construct_id}-stac-ready-dlq", retention_days=14),
            ),
        )
        self.stac_ready_queue.grant_send_messages(cogify_lambda.role)

        trigger_ingest_lambda.add_event_source(
            lambda_event_sources.SqsEventSource(
                self.stac_ready_queue,
                batch_size=10,
                max_batching_window=core.Duration.seconds(30),
                report_batch_item_failures=True,
            )
        )

    def _queue(
        self, name, visibility_timeout=30, dead_letter_queue=None, retention_days=4
    ):
        return sqs.Queue(
            self,
            name,
            queue_name=name,
            visibility_timeout=core.Duration.seconds(visibility_timeout),
            dead_letter_queue=dead_letter_queue,
            retention_period=core.Duration.days(retention_days),
        )

    @property
    def queues(self):
        return {
            "cogify_queue": self.cogify_queue,
            "stac_ready_queue": self.stac_ready_queue,
        }
