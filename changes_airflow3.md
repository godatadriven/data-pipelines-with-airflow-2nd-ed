1. Change: Default DAG Schedule changed to *None*
   Action: Verify if we mention the default schedule. If so, change.
2. Action: Mention airflow config lint.
3. Action: Run airflow config lint on all examples in all chapters to find any 2->3 deprecations
3. Change: Rename ``Dataset`` as ``Asset``
   Action: Rename where appropriate. (at the moment: chapter 3 and chapter 6)
4. Change: Support for SubDags is removed
   Action: verify we don't mention them anywhere. If we do, make appropriate change.
5. Change: days_ago removed
   Action: verify that we don't use this anymore. Chapter 7 still seems to have it.
6. Change: Deprecated `smtp_user` and `smtp_password` configuration. Needs to be a connection
   Action: chapter 14, update to use smtp connection
7. Change: Removed deprecated ``apply_defaults`` function from ``airflow/utils/decorators.py``.
   Action: we use this. Check what the fix is. There is none listed in the change notes. There is a ruff linting rule: AIR302
8. Change: Removed deprecated auth ``airflow.api.auth.backend.basic_auth`` from ``auth_backends``. Please use ``airflow.providers.fab.auth_manager.api.auth.backend.basic_auth`` instead.
   Action: we probably use this, will need to change. Probably chapter 16.
9. Change: Removed backfill job command cli option ``ignore-first-depends-on-past``. Its value always set to True. No replcaement cli option.
   Action: check if we explicitly mention this in chapter 3.
10. Change: Removed a set of deprecations in BaseOperator.
      - Parameter ``task_concurrency`` removed, please use ``max_active_tis_per_dag``.
      - Support for additional (not defined) arguments removed.
      - Support for trigger rule ``dummy`` removed. Please use ``always``.
      - Support for trigger rule ``none_failed_or_skipped`` removed. Please use ``none_failed_min_one_success``.
      - Support to load ``BaseOperatorLink`` via ``airflow.models.baseoperator`` module removed.
      - Config ``operators.allow_illegal_arguments`` removed.
   Action: verify whether this impacts us and change if needed.
11. Change: Removed deprecated metrics configuration.
    * Removed deprecated configuration ``statsd_allow_list`` from ``metrics``. Please use ``metrics_allow_list`` from ``metrics`` instead.
    * Removed deprecated configuration ``statsd_block_list`` from ``metrics``. Please use ``metrics_block_list`` from ``metrics`` instead.
    * Removed deprecated configuration ``statsd_on`` from ``scheduler``. Please use ``statsd_on`` from ``metrics`` instead.
    * Removed deprecated configuration ``statsd_host`` from ``scheduler``. Please use ``statsd_host`` from ``metrics`` instead.
    * Removed deprecated configuration ``statsd_port`` from ``scheduler``. Please use ``statsd_port`` from ``metrics`` instead.
    * Removed deprecated configuration ``statsd_prefix`` from ``scheduler``. Please use ``statsd_prefix`` from ``metrics`` instead.
    * Removed deprecated configuration ``statsd_allow_list`` from ``scheduler``. Please use ``statsd_allow_list`` from ``metrics`` instead.
    * Removed deprecated configuration ``stat_name_handler`` from ``scheduler``. Please use ``stat_name_handler`` from ``metrics`` instead.
    * Removed deprecated configuration ``statsd_datadog_enabled`` from ``scheduler``. Please use ``statsd_datadog_enabled`` from ``metrics`` instead.
    * Removed deprecated configuration ``statsd_datadog_tags`` from ``scheduler``. Please use ``statsd_datadog_tags`` from ``metrics`` instead.
    * Removed deprecated configuration ``statsd_datadog_metrics_tags`` from ``scheduler``. Please use ``statsd_datadog_metrics_tags`` from ``metrics`` instead.
    * Removed deprecated configuration ``statsd_custom_client_path`` from ``scheduler``. Please use ``statsd_custom_client_path`` from ``metrics`` instead.
    Action: Check if we need to do something. Chapter 14 would be where to look
12. Change: Move bash operators from airflow core to standard provider
    airflow.operators.bash.BashOperator`` → ``airflow.providers.standard.operators.bash.BashOperator
    Action: Change these imports. This probably holds for all standard operators (e.g. PythonOperator etc.)
13. Change: The SLA feature is removed in Airflow 3.0, to be replaced with Airflow Alerts in 3.1
    Action: Remove text/code, reference Airflow 3.1
14. Change: Removed ``logical_date`` arguments from functions and APIs for DAG run lookups to align with Airflow 3.0.
    The shift towards using ``run_id`` as the sole identifier for DAG runs eliminates the limitations of ``execution_date`` and ``logical_date``, particularly for dynamic DAG runs and cases where multiple runs occur at the same logical time. This change impacts database models, templates, and functions:

    - Removed ``logical_date`` arguments from public APIs and Python functions related to DAG run lookups.
    - ``run_id`` is now the exclusive identifier for DAG runs in these contexts.
    - ``ds``, ``ds_nodash``, ``ts``, ``ts_nodash``, ``ts_nodash_with_tz`` (and ``logical_date``) will no longer exist for non-scheduled DAG runs (i.e. manually triggered runs)
    - ``task_instance_key_str`` template variable has changed to use ``run_id``, not the logical_date. This means the value of it will change compared to 2.x, even for old runs
    Action: figure out what the impact is of this, update text and code.
15. Change: Default ``.airflowignore`` syntax changed to ``glob``
    Action: Verify our airflowignores to make sure we use the new syntax.
16. Change: Removed deprecated aliases support for providers.
    * Removed deprecated ``atlas`` alias support. Please use ``apache-atlas`` instead.
    * Removed deprecated ``aws`` alias support. Please use ``amazon`` instead.
    * Removed deprecated ``azure`` alias support. Please use ``microsoft-azure`` instead.
    * Removed deprecated ``cassandra`` alias support. Please use ``apache-cassandra`` instead.
    * Removed deprecated ``crypto`` alias support.
    * Removed deprecated ``druid`` alias support. Please use ``apache-druid`` instead.
    * Removed deprecated ``gcp`` alias support. Please use ``google`` instead.
    * Removed deprecated ``gcp-api`` alias support. Please use ``google`` instead.
    * Removed deprecated ``hdfs`` alias support. Please use ``apache-hdfs`` instead.
    * Removed deprecated ``hive`` alias support. Please use ``apache-hive`` instead.
    * Removed deprecated ``kubernetes`` alias support. Please use ``cncf-kubernetes`` instead.
    * Removed deprecated ``mssql`` alias support. Please use ``microsoft-mssql`` instead.
    * Removed deprecated ``pinot`` alias support. Please use ``apache-pinot`` instead.
    * Removed deprecated ``s3`` alias support. Please use ``amazon`` instead.
    * Removed deprecated ``spark`` alias support. Please use ``apache-spark`` instead.
    * Removed deprecated ``webhdfs`` alias support. Please use ``apache-webhdfs`` instead.
    * Removed deprecated ``winrm`` alias support. Please use ``microsoft-winrm`` instead.
    Action: check pip install requirements
17. Change: ``DAG.max_active_runs`` is now evaluated per-run
    Previously, this was evaluated across all runs of the dag. This behavior change was passed by lazy consensus.
    Vote thread: https://lists.apache.org/thread/9o84d3yn934m32gtlpokpwtbbmtxj47l.
    Action: Check if we need to change anything
18. Change: Move Airflow core triggers to standard provider. Move filesystem sensor to standard provider. Move ``TriggerDagRunOperator`` to standard provider. Move external task sensor to standard provider. Moving EmptyOperator from Airflow core to the ``standard`` provider.
    Action: update imports where appropriate.
19. Change: Configuration ``[core] strict_dataset_uri_validation`` is removed
    Asset URI with a defined scheme will now always be validated strictly, raising
    a hard error on validation failure.
    Action: Check if we use this
20. Change: Deprecated cli commands under ``db`` group removed
    The ``db init`` and ``db upgrade`` commands have been removed. Use ``db migrate`` instead to initialize or migrate the metadata database.
    Action: Check and change where needed.
21. Change: Standalone DAG processor is now required
    The scheduler is no longer able to parse DAGs itself - it relies on the standalone DAG processor (introduced in Airflow 2.3) to do it instead. You can start one by running ``airflow dag-processor``.
    Action: Update text, diagrams, code config
22. Change: Change how asset uris are accessed in inlet_events
    We used to be able to read asset uri through

    .. code-block:: python

    @task
    def access_inlet_events(inlet_events):
    print(inlet_events["uri"])

    Now we'll need to do

    .. code-block:: python

    @task
    def access_inlet_events(inlet_events):
    print(inlet_events["asset"]["uri"])
    Action: Update dataset material
23. Change: Replace the ``external_trigger`` check with ``DagRunType``, and update any logic that relies on ``external_trigger`` to use ``run_type`` instead.
    Action: Check if we use this with Datasets. If so, update.
24. Change: Auto data interval calculation is disabled by default
    Configurations ``[scheduler] create_cron_data_intervals`` and ``create_delta_data_intervals`` are now *False*
    by default. This means schedules specified using cron expressions or time deltas now have their logical date
    set to *when a new run can start* instead of one data interval before.
    Action: Check what this means and update where needed. Possibly code + text
25. Change: The new Airflow UI is now being served as part of the ``airflow api-server`` command and the ``airflow webserver`` command has been removed.
    Action: Update text + docker-compose
26. Change: Catchup is now disabled by default.
    Action: Update text, check any "days_ago" dags. These may be impacted.
27. Change: Removed auth backends. Auth backends are no longer used in Airflow 3. Please refer to documentation on how to use Airflow 3 public API.
    Action: Check
28. Change: Default connections no longer created by ``airflow db reset``
    When default connection creation was removed from the ``airflow db migrate`` command in in 2.7,
    ``airflow db reset`` was missed and still used the deprecated configuration option
    ``[database] load_default_connections``. ``airflow db reset`` no longer does, so after a DB reset you must call
    ``airflow connections create-default-connections`` explicitly if you'd like the default connections to be created.
    Action: Update text
29. Change: Support DAG versioning by introducing DAG Bundles
    Action: new feature, new examples, new text
