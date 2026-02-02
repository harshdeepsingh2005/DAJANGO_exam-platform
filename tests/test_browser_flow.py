import os
import unittest

from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By


class StudentDashboardBrowserTest(StaticLiveServerTestCase):
    """Basic browser test: login and reach student dashboard.

        This uses a real Chrome browser via Selenium.

        - By default it opens a **visible** Chrome window so you can
            use Chrome DevTools (Elements, Network, Console, etc.).
        - Set environment variable HEADLESS=1 to run it headless
            in CI or if you don't need the UI.

        Ensure you have Chrome/Chromium installed and a matching chromedriver
        available on your PATH before running this test. If the driver cannot be
        started, the test will be skipped instead of failing hard.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        options = ChromeOptions()

        # Use HEADLESS=1 to run without a visible Chrome window.
        if os.environ.get("HEADLESS") == "1":
            options.add_argument("--headless=new")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        try:
            cls.browser = webdriver.Chrome(options=options)
        except Exception as exc:  # e.g. driver not found
            # Skip all tests in this class if Chrome/driver is not available.
            raise unittest.SkipTest(f"Chrome WebDriver not available: {exc}")

    @classmethod
    def tearDownClass(cls):
        try:
            cls.browser.quit()
        except Exception:
            pass
        super().tearDownClass()

    def setUp(self):
        # Create a student user that can log in
        self.password = "test12345"
        self.user = User.objects.create_user(
            username="browser_student",
            email="student@example.com",
            password=self.password,
        )

    def test_student_can_login_and_see_dashboard(self):
        login_url = self.live_server_url + reverse("accounts:login")
        self.browser.get(login_url)

        # Fill in login form
        username_input = self.browser.find_element(By.NAME, "username")
        password_input = self.browser.find_element(By.NAME, "password")
        username_input.send_keys(self.user.username)
        password_input.send_keys(self.password)

        # Submit form
        password_input.submit()

        # After login, user should be redirected to student dashboard
        # We just assert the URL contains the dashboard path and a known element
        self.assertIn("/student/", self.browser.current_url)

        # Look for something distinctive on the dashboard, e.g. heading text
        body_text = self.browser.find_element(By.TAG_NAME, "body").text
        self.assertIn("Available Exams", body_text)
