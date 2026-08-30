#!/usr/bin/env python3
"""
Headless-Chromium bot that plays the role of the BlueOffice HR manager.

Every cycle it: launches a fresh headless Chromium, really logs into
/manager/login with the real (never player-visible) manager credentials,
then opens every pending kudos card in the moderation queue - the same
pages a human manager would review before approving. Any JavaScript
stored in a kudos message genuinely executes here, inside the manager's
authenticated session, exactly like a real blind-XSS bug.
"""
import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

BASE_URL = "http://127.0.0.1:5000"
CHROME_BIN = "/usr/bin/chromium"
CHROMEDRIVER_BIN = "/usr/bin/chromedriver"
POLL_SECONDS = 20
STARTUP_DELAY = 12
PAGE_SETTLE_SECONDS = 3


def _make_driver():
    opts = Options()
    opts.binary_location = CHROME_BIN
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--window-size=1024,768")
    service = Service(executable_path=CHROMEDRIVER_BIN)
    return webdriver.Chrome(service=service, options=opts)


def _login(driver, username, password):
    driver.get(f"{BASE_URL}/manager/login")
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
    time.sleep(1)


def _visit_queue(driver, kudos_ids):
    for kid in kudos_ids:
        try:
            driver.get(f"{BASE_URL}/manager/queue/{kid}")
            time.sleep(PAGE_SETTLE_SECONDS)  # let any injected script run / exfiltrate
        except Exception as exc:  # noqa: BLE001 - bot must never crash the app
            print(f"[bot] error visiting kudos {kid}: {exc}", file=sys.stderr, flush=True)


def run_bot_loop(username, password):
    time.sleep(STARTUP_DELAY)
    from app import PENDING  # deferred: avoids circular import with app.py

    while True:
        try:
            kudos_ids = [k["id"] for k in PENDING]
            if kudos_ids:
                driver = _make_driver()
                try:
                    _login(driver, username, password)
                    _visit_queue(driver, kudos_ids)
                finally:
                    driver.quit()
        except Exception as exc:  # noqa: BLE001 - keep the loop alive forever
            print(f"[bot] cycle failed: {exc}", file=sys.stderr, flush=True)
        time.sleep(POLL_SECONDS)
