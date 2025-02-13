from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.support.ui import Select
from login.models import User as myUser
import bcrypt

class AdminCreateEventTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        service = Service(ChromeDriverManager().install())
        cls.browser = webdriver.Chrome(service=service)

        User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpassword"
        )
        print("Utworzono konto administratora.")

        hashed_password = bcrypt.hashpw("hashed_password_example".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cls.user = myUser.objects.create(
            email="testuser@gmail.com",
            passwordHash=hashed_password
        )
        print("Stworzono użytkownika testowego.")

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def test_admin_creates_event(self):
        # Logowanie do panelu admina

        self.browser.get(f"{self.live_server_url}/admin/")
        time.sleep(1)
        self.browser.find_element(By.NAME, "username").send_keys("admin")
        time.sleep(1)
        self.browser.find_element(By.NAME, "password").send_keys("adminpassword")
        time.sleep(1)
        self.browser.find_element(By.CSS_SELECTOR, "button.btn.btn-primary.btn-block").click()
        time.sleep(2)
        print("Zalogowano jako administrator.")

        # Dodanie lokalizacji

        self.browser.find_element(By.LINK_TEXT, "Places").click()
        time.sleep(1)
        self.browser.find_element(By.LINK_TEXT, "Add place").click()
        time.sleep(1)
        self.browser.find_element(By.NAME, "name").send_keys("Test Arena")
        time.sleep(1)
        self.browser.find_element(By.NAME, "address").send_keys("Testowa 123")
        time.sleep(1)
        self.browser.find_element(By.NAME, "city").send_keys("Test City")
        time.sleep(1)
        self.browser.find_element(By.NAME, "country").send_keys("Test Country")
        time.sleep(1)
        self.browser.find_element(By.NAME, "_save").click()
        print("Dodano lokalizację.")

        # Dodanie sektora

        self.browser.get(f"{self.live_server_url}/admin/sectors/sector/add/")
        self.browser.find_element(By.NAME, "name").send_keys("A")
        time.sleep(1)
        select_place = Select(self.browser.find_element(By.NAME, "place"))
        select_place.select_by_visible_text("Test Arena")
        time.sleep(1)
        self.browser.find_element(By.NAME, "price").send_keys("10")
        time.sleep(1)
        self.browser.find_element(By.NAME, "_save").click()
        time.sleep(2)
        print("Dodano sektor.")

        # Dodawanie rzędu
        self.browser.get(f"{self.live_server_url}/admin/rows/row/add/")
        time.sleep(2)  # Opóźnienie, aby upewnić się, że skrypt JS się załadował

        # Wybór miejsca z rozwijanej listy
        place_select = Select(self.browser.find_element(By.NAME, "place"))
        place_select.select_by_visible_text("Test Arena")
        time.sleep(2)

        # Wybór sektora z rozwijanej listy
        sector_select = Select(WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.NAME, "sector"))
        ))
        sector_select.select_by_visible_text("A")
        time.sleep(2)

        # Wprowadzenie liczby rzędów
        row_count_field = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.NAME, "row_count"))
        )
        row_count_field.send_keys("2")
        time.sleep(2)

        # Zapisanie formularza
        self.browser.find_element(By.CSS_SELECTOR, "input[value='Save']").click()
        print("Dodano rząd.")
        time.sleep(2)

        # Dodawanie miejsca
        self.browser.get(f"{self.live_server_url}/admin/seats/seat/add/")
        time.sleep(2)  # Upewnienie się, że skrypt JS się załadował

        # Wybór miejsca z rozwijanej listy
        place_select = Select(self.browser.find_element(By.NAME, "place"))
        place_select.select_by_visible_text("Test Arena")
        time.sleep(2)

        # Wybór sektora z rozwijanej listy
        sector_select = Select(WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.NAME, "sector"))
        ))
        sector_select.select_by_visible_text("A")
        time.sleep(2)

        # Wybór rzędu z rozwijanej listy (dynamiczne ładowanie)
        row_select = WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.NAME, "row"))
        )
        time.sleep(2)

        # Wybierz opcję "Rząd 1"
        Select(row_select).select_by_visible_text("Rząd 1")
        time.sleep(2)

        # Wprowadzenie liczby miejsc
        seat_count_field = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.NAME, "seat_count"))
        )
        seat_count_field.send_keys("10")
        time.sleep(2)

        # Zapisanie formularza
        self.browser.find_element(By.CSS_SELECTOR, "input[value='Save']").click()
        print("Dodano miejsca.")
        time.sleep(2)

        # Dodanie wydarzenia
        self.browser.get(f"{self.live_server_url}/admin/events/event/add/")
        self.browser.find_element(By.NAME, "title").send_keys("Test Event")
        time.sleep(1)
        self.browser.find_element(By.NAME, "start_0").send_keys("2024-12-31")
        time.sleep(1)
        self.browser.find_element(By.NAME, "start_1").send_keys("18:00")
        time.sleep(1)
        select_place = Select(self.browser.find_element(By.NAME, "place"))
        select_place.select_by_visible_text("Test Arena")
        time.sleep(1)
        self.browser.find_element(By.NAME, "_save").click()
        time.sleep(2)
        print("Dodano wydarzenie.")

        # Przejście do strony logowania

        self.browser.get(f"{self.live_server_url}/login/")
        time.sleep(2)

        # Logowanie jako użytkownik

        self.browser.find_element(By.NAME, "email").send_keys("testuser@gmail.com")
        self.browser.find_element(By.NAME, "password").send_keys("hashed_password_example")
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)
        print("Zalogowano jako użytkownik.")

        # Sprawdzenie, czy wydarzenie jest widoczne
        
        time.sleep(2)
        event = WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".event-card .event-title"))
        )
        self.assertEqual(event.text, "Test Event")
        print("Wydarzenie jest widoczne na stronie głównej.")
