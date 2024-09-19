from pytest_docker_tools import fetch

postgres_image = fetch(repository="postgres:16-alpine")

def test_call_fixture(postgres_image):
    print(postgres_image.id)
