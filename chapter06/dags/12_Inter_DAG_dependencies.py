import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

# ================================================ EXAMPLE 1 =================================================

with DAG(
    dag_id="figure_6_17_example_1_dag_1",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="0 0 * * *",
):
    
    EmptyOperator(task_id="etl") >> TriggerDagRunOperator(
        task_id="trigger_dag2",
        trigger_dag_id="figure_6_17_example_1_dag_2",
    )
    
with DAG(
    dag_id="figure_6_17_example_1_dag_2",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=None,
):

    PythonOperator(task_id="report", python_callable=lambda: print("hello"))

# ================================================ EXAMPLE 2 =================================================

with DAG(
    dag_id="figure_6_17_example_2_dag_1",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="0 0 * * *",
) as example_2_dag_1:
    ...


with DAG(
    dag_id="figure_6_17_example_2_dag_2",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="0 0 * * *",
) as example_2_dag_2:
    ...
    
with DAG(
    dag_id="figure_6_17_example_2_dag_3",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="0 0 * * *",
) as example_2_dag_3:
    ...
    
with DAG(
    dag_id="figure_6_17_example_2_dag_4",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=None,
):
    PythonOperator(task_id="report", python_callable=lambda: print("hello"))

for dag_ in [example_2_dag_1, example_2_dag_2, example_2_dag_3]:
    EmptyOperator(task_id="etl", dag=dag_) >> TriggerDagRunOperator(
        task_id="trigger_dag4", trigger_dag_id="figure_6_17_example_2_dag_4", dag=dag_
    )


# ================================================ EXAMPLE 3 =================================================

with DAG(
    dag_id="figure_6_17_example_3_dag_1",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="0 0 * * *",
):
    EmptyOperator(task_id="etl") >> [
        TriggerDagRunOperator(
            task_id="trigger_dag2",
            trigger_dag_id="figure_6_17_example_3_dag_2",
        ),
        TriggerDagRunOperator(
            task_id="trigger_dag3",
            trigger_dag_id="figure_6_17_example_3_dag_3",
        ),
        TriggerDagRunOperator(
            task_id="trigger_dag4",
            trigger_dag_id="figure_6_17_example_3_dag_4",
        ),
    ]

with DAG(
    dag_id="figure_6_17_example_3_dag_2",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=None,
):
    PythonOperator(task_id="report", python_callable=lambda: print("hello"))

    
with DAG(
    dag_id="figure_6_17_example_3_dag_3",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=None,
):
    PythonOperator(task_id="report", python_callable=lambda: print("hello"))

    
with DAG(
    dag_id="figure_6_17_example_3_dag_4",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=None,
):   
    PythonOperator(task_id="report", python_callable=lambda: print("hello"))
