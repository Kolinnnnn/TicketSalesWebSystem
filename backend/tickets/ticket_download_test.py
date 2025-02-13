from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from orders.models import Order
from login.models import User
from events.models import Event
from place.models import Place
from sectors.models import Sector
from rows.models import Row
from seats.models import Seat
from tickets.models import TicketCategory
from decimal import Decimal
from datetime import datetime
import bcrypt
import time

class TicketRetrievalTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        service = Service(ChromeDriverManager().install())
        cls.browser = webdriver.Chrome(service=service)

        # Tworzenie użytkownika
        hashed_password = bcrypt.hashpw("hashed_password_example".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cls.user = User.objects.create(
            email="testuser@gmail.com",
            passwordHash=hashed_password
        )

        # Tworzenie danych zamówienia
        cls.place = Place.objects.create(
            name="Test Arena",
            address="123 Test St.",
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
        cls.seat = Seat.objects.create(
            name="Seat 1",
            row=cls.row,
            sector=cls.sector,
            place=cls.place,
            is_available=False
        )
        cls.ticket_category = TicketCategory.objects.create(category="normal")

        cls.order = Order.objects.create(
            user=cls.user,
            event=cls.event,
            seat=cls.seat,
            ticket_type=cls.ticket_category,
            is_paid=True,
            price=Decimal('100.00')
        )

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def test_view_and_download_ticket(self):
        # Logowanie użytkownika

        self.browser.get(f"{self.live_server_url}/login/")
        self.browser.find_element(By.NAME, "email").send_keys("testuser@gmail.com")
        self.browser.find_element(By.NAME, "password").send_keys("hashed_password_example")
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)

        # Przejdź do strony profilu

        self.browser.get(f"{self.live_server_url}/profile/")
        time.sleep(1)

        # Kliknij VIEW (Widok biletu)

        view_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "View"))
        )
        view_button.click()
        time.sleep(1)
        print("Przejście do szczegółów biletu.")

        # Sprawdzenie szczegółów biletu

        ticket_details = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ticket-details"))
        )
        self.assertIn("Sector: A", ticket_details.text)
        print("Szczegóły biletu wyświetlone poprawnie.")
        time.sleep(1)

        # Powrót do profilu

        self.browser.back()
        time.sleep(1)
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ticket-card"))
        )
        print("Powrót do profilu użytkownika.")

        # Kliknij DOWNLOAD (Pobieranie biletu)
        
        download_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Download"))
        )
        download_button.click()
        time.sleep(3)
        print("Próba pobrania biletu.")

        print("Bilet został pobrany.")

