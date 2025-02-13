from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.common.exceptions import TimeoutException
from tickets.models import TicketCategory
from login.models import User
from events.models import Event
from place.models import Place
from sectors.models import Sector
from rows.models import Row
from seats.models import Seat
import bcrypt
import time
from decimal import Decimal
from datetime import datetime
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

class TicketPurchaseTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        service = Service(ChromeDriverManager().install())
        cls.browser = webdriver.Chrome(service=service)

        # Tworzenie testowego użytkownika i danych
        # hashed_password = bcrypt.hashpw("user1".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        # cls.test_user = User.objects.create(
        #     email="user1@gmail.com",
        #     passwordHash=hashed_password
        # )

        cls.place = Place.objects.create(
            name="Test Stadium",
            address="123 Test Street",
            city="Test City",
            country="Test Country"
        )

        cls.event = Event.objects.create(
            title="Test Event",
            start=datetime(2024, 12, 31, 18, 0),
            place=cls.place
        )

        cls.sector = Sector.objects.create(
            name="A",
            place=cls.place,
            price=Decimal('100.00')
        )

        cls.row = Row.objects.create(
            name="1",
            sector=cls.sector,
            place=cls.place
        )

        cls.seat1 = Seat.objects.create(
            name="Seat 1",
            row=cls.row,
            sector=cls.sector,
            place=cls.place,
            is_available=True
        )

        cls.seat2 = Seat.objects.create(
            name="Seat 2",
            row=cls.row,
            sector=cls.sector,
            place=cls.place,
            is_available=True
        )

        cls.ticket_category = TicketCategory.objects.create(
            category="discount"
        )

        cls.ticket_category_normal = TicketCategory.objects.create(
            category="normal"
        )
        
    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def test_add_ticket_to_cart(self):
        # Otwórz stronę rejestracji

        self.browser.get(f"{self.live_server_url}/register/")
        time.sleep(2)

        # Wypełnij formularz rejestracji


        self.browser.find_element(By.NAME, "email").send_keys("user1@gmail.com")
        self.browser.find_element(By.NAME, "password").send_keys("user1")
        self.browser.find_element(By.NAME, "confirm_password").send_keys("user1")
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        print("Użytkownik został zarejestrowany.")

        time.sleep(2)

        # Otwórz stronę logowania
        self.browser.get(f"{self.live_server_url}/login/")
        time.sleep(2)

        # Zaloguj się
        username_input = self.browser.find_element(By.NAME, "email")
        password_input = self.browser.find_element(By.NAME, "password")
        username_input.send_keys("user1@gmail.com")
        password_input.send_keys("user1")
        password_input.send_keys(Keys.RETURN)
        print("Zalogowano jako user1.")

        time.sleep(2)

        # Dodaj bilety do koszyka

        self.add_ticket_to_cart(ticket_category="discount", seat_index=1)
        self.add_ticket_to_cart(ticket_category="normal", seat_index=1)
        self.go_to_cart()

        # Sprawdź sumę w koszyku
        
        total_price_element = WebDriverWait(self.browser, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".total-price-container h4"))
        )
        total_price_text = total_price_element.text.strip()
        assert total_price_text == "Total Price: 150.00 zł", f"Oczekiwano: 'Total Price: 150.00 zł', Znaleziono: '{total_price_text}'"
        print("Suma w koszyku 150.00 zł została potwierdzona.")

        # Przejdź do płatności

        checkout_button = WebDriverWait(self.browser, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-success"))
        )
        self.browser.execute_script("arguments[0].scrollIntoView(true);", checkout_button)
        time.sleep(1)
        checkout_button.click()
        print("Kliknięto 'Proceed to Checkout'.")

        # Sprawdź, czy został przekierowany na stronę Stripe
        
        WebDriverWait(self.browser, 30).until(
            EC.url_contains("checkout.stripe.com")
        )
        assert "checkout.stripe.com" in self.browser.current_url, "Nie przekierowano na stronę Stripe"
        print("Test zakończony pomyślnie: użytkownik został przekierowany na Stripe.")

    def add_ticket_to_cart(self, ticket_category, seat_index):
        # Przejdź do strony kupowania biletu


        self.browser.get(f"{self.live_server_url}/event/{self.event.id}/buy_ticket/")
        time.sleep(2)

        # Wybierz kategorię biletu

        WebDriverWait(self.browser, 15).until(
            EC.presence_of_element_located((By.ID, "ticket_category"))
        )
        category_select = Select(self.browser.find_element(By.ID, "ticket_category"))
        category_select.select_by_value(ticket_category)
        print(f"Wybrano kategorię biletu: {ticket_category}.")

        time.sleep(2)

        # Wybierz sektor

        WebDriverWait(self.browser, 15).until(
            lambda driver: len(Select(driver.find_element(By.ID, "sector")).options) > 1
        )
        sector_select = Select(self.browser.find_element(By.ID, "sector"))
        sector_select.select_by_visible_text("A")
        print("Wybrany sektor:", sector_select.first_selected_option.text)

        time.sleep(2)

        # Wybierz rząd
        WebDriverWait(self.browser, 15).until(
            lambda driver: len(Select(driver.find_element(By.ID, "row")).options) > 1
        )
        row_select = Select(self.browser.find_element(By.ID, "row"))
        row_select.select_by_index(1)
        print("Wybrany rząd:", row_select.first_selected_option.text)

        time.sleep(2)

        # Wybierz miejsce
        WebDriverWait(self.browser, 30).until(
            lambda driver: len(Select(driver.find_element(By.ID, "seat")).options) > seat_index
        )
        seat_select = Select(self.browser.find_element(By.ID, "seat"))
        print("Dostępne miejsca:", [option.text for option in seat_select.options])
        seat_select.select_by_index(seat_index)
        print(f"Wybrane miejsce: {seat_select.first_selected_option.text}")

        time.sleep(2)

        # Kliknij przycisk dodawania do koszyka
        
        add_to_cart_button = self.browser.find_element(By.NAME, "add_to_cart")
        self.browser.execute_script("arguments[0].scrollIntoView(true);", add_to_cart_button)
        WebDriverWait(self.browser, 15).until(EC.element_to_be_clickable((By.NAME, "add_to_cart")))

        try:
            add_to_cart_button.click()
            print("Kliknięto 'Add to Cart'.")
        except Exception as e:
            print("Problem z kliknięciem 'Add to Cart':", str(e))
            self.browser.execute_script("arguments[0].click();", add_to_cart_button)
            print("Kliknięto 'Add to Cart' przy pomocy JavaScript.")

    def go_to_cart(self):
        # Przejdź do koszyka
        self.browser.get(f"{self.live_server_url}/cart/")
        print("Przeniesiono do koszyka.")
        time.sleep(2)