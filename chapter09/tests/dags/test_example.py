from airflow.operators.bash import BashOperator


def test_example():
    task = BashOperator(
        task_id="test", bash_command="echo 'hello!'"
    )
    result = task.execute(context={})
    assert result == "hello!"
