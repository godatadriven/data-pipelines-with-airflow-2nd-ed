import random

from faker import Faker
from fastapi import FastAPI

app = FastAPI()
faker = Faker()


def _generate_latest_reviews(max_n=10):
    number_of_reviews = random.randint(1, max_n)

    return [{
        "movie": f"{faker.word()} {faker.word()}",
        "rating": random.randint(1, 5)
    } for i in range(number_of_reviews)]


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/reviews/latest")
def reviews_latest():
    return _generate_latest_reviews()
