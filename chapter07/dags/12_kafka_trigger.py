"""
    Figure: 6.5
"""

from airflow.sdk import DAG, AssetWatcher, Asset
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.common.messaging.triggers.msg_queue import MessageQueueTrigger

trigger = MessageQueueTrigger(
    queue="kafka://kafka:9092/events",
    apply_function="custom.kafka_util.apply_function",
)


asset = Asset("kafka_queue_asset", watchers=[AssetWatcher(name="kafka_watcher", trigger=trigger)])

with DAG(
        dag_id="12_kafka_trigger",
        schedule=[asset],
        description="A batch workflow for ingesting supermarket promotions data, demonstrating the Message Queue Trigger.",
):
    create_metrics = EmptyOperator(task_id="create_metrics")

    copy = EmptyOperator(task_id=f"copy_to_raw_supermarket_1")
    process = EmptyOperator(task_id=f"process_supermarket_1")
    copy >> process >> create_metrics
