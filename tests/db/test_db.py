import pytest
from utils.db_utils import DBUtils
from data.data_factory import DataFactory


@pytest.fixture(scope="module")
def db():
    _db = DBUtils()
    _db.setup_test_db()
    yield _db
    _db.cleanup()


@pytest.fixture(scope="function")
def test_user(db):
    user    = DataFactory.generate_user()
    user_id = db.insert("users", {
        "name":   f"{user['first_name']} {user['last_name']}",
        "email":  user["email"],
        "role":   "customer",
        "active": 1
    })
    user["id"] = user_id
    yield user
    db.delete_where("users", {"email": user["email"]})


class TestDatabaseLayer:

    @pytest.mark.db
    @pytest.mark.smoke
    def test_users_table_exists(self, db):
        db.assert_table_exists("users")

    @pytest.mark.db
    @pytest.mark.smoke
    def test_products_table_exists(self, db):
        db.assert_table_exists("products")

    @pytest.mark.db
    @pytest.mark.smoke
    def test_orders_table_exists(self, db):
        db.assert_table_exists("orders")

    @pytest.mark.db
    def test_insert_user(self, db, test_user):
        db.assert_record_exists(
            "users",
            {"email": test_user["email"]}
        )

    @pytest.mark.db
    def test_user_has_correct_role(self, db, test_user):
        db.assert_column_value(
            "users", "role",
            {"email": test_user["email"]},
            "customer"
        )

    @pytest.mark.db
    def test_user_is_active(self, db, test_user):
        db.assert_column_value(
            "users", "active",
            {"email": test_user["email"]},
            1
        )

    @pytest.mark.db
    def test_fetch_user_by_email(self, db, test_user):
        row = db.fetch_one(
            "SELECT * FROM users WHERE email = :email",
            {"email": test_user["email"]}
        )
        assert row is not None
        assert row["email"] == test_user["email"]
        print(f"Fetched: {row['name']} - {row['email']}")

    @pytest.mark.db
    def test_update_user_role(self, db, test_user):
        db.execute(
            "UPDATE users SET role = :role WHERE email = :email",
            {"role": "admin", "email": test_user["email"]}
        )
        db.assert_column_value(
            "users", "role",
            {"email": test_user["email"]},
            "admin"
        )

    @pytest.mark.db
    def test_delete_user(self, db, test_user):
        db.delete_where("users", {"email": test_user["email"]})
        db.assert_record_not_exists(
            "users", {"email": test_user["email"]}
        )

    @pytest.mark.db
    def test_insert_product(self, db):
        product = DataFactory.generate_product()
        db.insert("products", {
            "name":     product["name"],
            "price":    product["price"],
            "stock":    100,
            "category": "electronics"
        })
        db.assert_record_exists("products", {"name": product["name"]})
        db.delete_where("products", {"name": product["name"]})

    @pytest.mark.db
    def test_bulk_insert_count(self, db):
        users  = [DataFactory.generate_user() for _ in range(3)]
        before = db.count_rows("users")
        for u in users:
            db.insert("users", {
                "name":  f"{u['first_name']} {u['last_name']}",
                "email": u["email"],
                "role":  "customer"
            })
        after = db.count_rows("users")
        assert after == before + 3
        print(f"Bulk insert: {before} → {after}")
        for u in users:
            db.delete_where("users", {"email": u["email"]})