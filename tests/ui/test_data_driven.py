import pytest
import openpyxl
import json
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils.wait_utils import WaitUtils
from data.data_factory import DataFactory


def get_excel_data():
    """Read test data from Excel file."""
    path = Path("data/excel/search_data.xlsx")
    wb   = openpyxl.load_workbook(path)
    ws   = wb.active
    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0]:
            rows.append(row)
    return rows


def get_json_data():
    """Read test data from JSON file."""
    return DataFactory.get_json("users")


class TestDataDriven:

    # ── Excel Data Driven ─────────────────────────────────────────────────────

    @pytest.mark.ui
    @pytest.mark.parametrize("topic,expected",
                             get_excel_data())
    def test_search_from_excel(self, driver, topic, expected):
        """
        Data comes from Excel file.
        Each row in Excel = one test case.
        """
        print(f"\nTesting search: {topic}")
        driver.get("https://www.google.com")
        wait   = WaitUtils(driver)
        search = wait.wait_for_element_visible(
            (By.NAME, "q")
        )
        search.clear()
        search.send_keys(topic)
        search.send_keys(Keys.RETURN)
        wait.wait_for_url_contains(expected)
        assert expected in driver.current_url
        print(f"PASS: '{topic}' search worked!")

    # ── JSON Data Driven ──────────────────────────────────────────────────────

    @pytest.mark.ui
    def test_json_fixture_loads(self, driver):
        """Verify JSON test data loads correctly."""
        users = get_json_data()
        assert "valid_user" in users
        assert "admin_user" in users
        assert "invalid_user" in users
        assert "@" in users["valid_user"]["email"]
        print(f"JSON data loaded: {users['valid_user']['email']}")

    # ── Faker Data Driven ─────────────────────────────────────────────────────

    @pytest.mark.ui
    @pytest.mark.parametrize("execution", range(3))
    def test_faker_search_random(self, driver, execution):
        """
        Runs 3 times with random search terms from Faker.
        Tests the framework handles dynamic data.
        """
        from faker import Faker
        fake  = Faker()
        topic = fake.job()
        print(f"\nRandom search #{execution+1}: {topic}")

        driver.get("https://www.google.com")
        wait   = WaitUtils(driver)
        search = wait.wait_for_element_visible(
            (By.NAME, "q")
        )
        search.clear()
        search.send_keys(topic)
        search.send_keys(Keys.RETURN)
        wait.wait_for_url_contains("search")
        assert "search" in driver.current_url
        print(f"PASS: Random search '{topic}' worked!")