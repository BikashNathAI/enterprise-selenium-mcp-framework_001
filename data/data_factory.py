import json
from pathlib import Path
from faker import Faker
from config.config import config

fake = Faker()


class DataFactory:

    DATA_DIR = config.DATA_DIR

    @classmethod
    def get_json(cls, fixture_name: str) -> dict:
        path = cls.DATA_DIR / "json" / f"{fixture_name}.json"
        if not path.exists():
            raise FileNotFoundError(f"Fixture not found: {path}")
        with open(path) as f:
            return json.load(f)

    @classmethod
    def generate_user(cls, role: str = "customer") -> dict:
        return {
            "first_name": fake.first_name(),
            "last_name":  fake.last_name(),
            "email":      fake.email(),
            "password":   fake.password(length=12),
            "phone":      fake.phone_number(),
            "role":       role,
        }