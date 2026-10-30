"""Selenium end-to-end test. Skipped automatically if Chrome is unavailable."""
import threading

import pytest
from werkzeug.serving import make_server

from app import create_app

selenium = pytest.importorskip("selenium")
from selenium import webdriver  # noqa: E402
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402


@pytest.fixture
def live_server(tmp_path):
    app = create_app({"DB_PATH": str(tmp_path / "e2e.db"), "TESTING": True})
    server = make_server("127.0.0.1", 5055, app)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield "http://127.0.0.1:5055"
    server.shutdown()


@pytest.fixture
def driver():
    opts = webdriver.ChromeOptions()
    for a in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage"):
        opts.add_argument(a)
    try:
        d = webdriver.Chrome(options=opts)
    except Exception:
        pytest.skip("Chrome/driver not available")
    yield d
    d.quit()


def test_add_book_through_ui(live_server, driver):
    driver.get(live_server)
    driver.find_element(By.ID, "title").send_keys("Clean Code")
    driver.find_element(By.ID, "author").send_keys("Robert Martin")
    driver.find_element(By.ID, "copies").send_keys("3")
    driver.find_element(By.ID, "add").click()
    WebDriverWait(driver, 5).until(
        EC.text_to_be_present_in_element((By.ID, "book-list"), "Clean Code"))
