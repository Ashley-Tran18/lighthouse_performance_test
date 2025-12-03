# base_test.py
from selenium import webdriver
from utils.config_reader import ConfigReader
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pytest


class BaseTest:
    @pytest.fixture(autouse=True)
    def driver(self,request):
        
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--incognito")
        prefs = {
            "credentials_enable_service": False,         # Tắt dịch vụ lưu mật khẩu
            "profile.password_manager_enabled": False    # Tắt gợi ý lưu mật khẩu
        }
        options.add_experimental_option("prefs", prefs)
        
        # Các args cho Linux/headless
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')  # Thêm để ổn định headless
        options.add_argument('--disable-features=VizDisplayCompositor')  # Fix lỗi render
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(service=Service(), options=options)
        
        base_url = ConfigReader.get_base_url()
        self.driver.get(base_url)

        # Cho phép các class test kế thừa sử dụng driver
        request.cls.driver = self.driver
        yield
        self.driver.quit()



