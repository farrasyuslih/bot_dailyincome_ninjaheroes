from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.action_chains import ActionChains
import time
import logging
import os
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NinjaHeroesBot:
    def __init__(self, email, password, server_choice, headless=False):
        self.email = email
        self.password = password
        self.server_choice = server_choice
        self.driver = None
        self.headless = headless
        
    def setup_driver(self):
        """Setup Chrome driver dengan opsi yang diperlukan"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
    
        # Opsi tambahan untuk stabilitas
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(5)  # Dikurangi dari 10 ke 5 detik
            logger.info("Driver berhasil diinisialisasi")
        except Exception as e:
            logger.error(f"Error saat setup driver: {e}")
            raise

    def find_login_button(self):
        """Step 1: Mencari tombol login untuk memunculkan popup login form"""
        logger.info("🔍 Step 1: Mencari tombol login Ninja Heroes...")
        
        # Selector untuk tombol login berdasarkan HTML yang diberikan
        login_button_selectors = [
            # Selector utama berdasarkan HTML yang diberikan
            "a.btn.btn-login.login-shinobi.loginMethod",
            "a[class='btn btn-login login-shinobi loginMethod']",
            ".btn.btn-login.login-shinobi.loginMethod",
            ".loginMethod",
            ".login-shinobi",
            
            # Alternatif berdasarkan kombinasi class
            "a.btn-login.loginMethod",
            "a.login-shinobi",
            "a[href='#'].btn-login",
            "a[href='#'].loginMethod",
            
            # Berdasarkan text content
            "//a[contains(@class, 'loginMethod') and text()='LOGIN']",
            "//a[contains(@class, 'btn-login') and text()='LOGIN']",
            "//a[contains(@class, 'login-shinobi') and text()='LOGIN']",
            "//a[contains(text(), 'LOGIN') and contains(@class, 'btn')]",
            
            # Fallback selectors
            "a[href='#']:contains('LOGIN')",
            ".btn:contains('LOGIN')",
            "//a[@href='#' and contains(text(), 'LOGIN')]",
            "//a[contains(@class, 'btn') and contains(text(), 'LOGIN')]",
            
            # Generic fallback
            "a[href*='login']",
            "button:contains('Login')",
            "//a[contains(text(), 'Login')]",
            "//button[contains(text(), 'Login')]",
            ".login-btn",
            "#login-btn",
            "[data-toggle='modal'][data-target*='login']",
            "//a[@href='#' and contains(@onclick, 'login')]",
        ]
        
        for selector in login_button_selectors:
            try:
                if selector.startswith("//"):
                    element = self.driver.find_element(By.XPATH, selector)
                else:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                
                if element.is_displayed() and element.is_enabled():
                    logger.info(f"✅ Tombol login ditemukan dengan selector: {selector}")
                    return element
                    
            except (NoSuchElementException, Exception):
                continue
        
        logger.error("❌ Tombol login tidak ditemukan dengan semua selector")
        self.take_screenshot("login_button_not_found.png")
        return None

    def fill_login_form(self):
        """Step 2: Mengisi form email dan password lalu submit"""
        logger.info("📝 Step 2: Mengisi form login...")
        
        try:
            # Tunggu modal login form benar-benar muncul dan siap
            logger.info("⏳ Menunggu modal login form siap...")
            
            # Tunggu modal dengan ID LoginForm muncul dan visible
            modal_wait = WebDriverWait(self.driver, 0.2)  # Dikurangi dari 15 ke 10
            modal_wait.until(EC.presence_of_element_located((By.ID, "LoginForm")))
            modal_wait.until(EC.visibility_of_element_located((By.ID, "LoginForm")))
            
            # time.sleep(1)  # Dikurangi dari 2 ke 1 detik
            
            # Focus ke dalam modal
            modal = self.driver.find_element(By.ID, "LoginForm")
            self.driver.execute_script("arguments[0].focus();", modal)
            
            # Cari field email dalam modal
            email_selectors = [
                "#LoginForm input[name='email']",
                "#LoginForm input[type='email']",
                "#LoginForm input[placeholder*='email']",
                "#LoginForm input[placeholder*='Email']",
                "#LoginForm #email",
                ".modal input[name='email']",
                ".modal input[type='email']"
            ]
            
            email_field = None
            for selector in email_selectors:
                try:
                    email_field = modal_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    if email_field.is_displayed():
                        break
                except:
                    continue
            
            if not email_field:
                raise Exception("Field email tidak ditemukan dalam modal")
            
            # Cari field password dalam modal
            password_selectors = [
                "#LoginForm input[type='password']",
                ".modal input[type='password']"
            ]
            
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = modal_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    if password_field.is_displayed():
                        break
                except:
                    continue
            
            if not password_field:
                raise Exception("Field password tidak ditemukan dalam modal")
            
            # Input email dengan scroll ke element
            logger.info("📧 Memasukkan email...")
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", email_field)
            time.sleep(0.2)  # Dikurangi dari 0.5 ke 0.2
            email_field.clear()
            time.sleep(0.2)  # Dikurangi dari 0.5 ke 0.2
            email_field.send_keys(self.email)
            
            time.sleep(0.5)  # Dikurangi dari 1 ke 0.5
            
            # Input password
            logger.info("🔐 Memasukkan password...")
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", password_field)
            time.sleep(0.2)  # Dikurangi dari 0.5 ke 0.2
            password_field.clear()
            time.sleep(0.2)  # Dikurangi dari 0.5 ke 0.2
            password_field.send_keys(self.password)
            
            time.sleep(0.5)  # Dikurangi dari 1 ke 0.5
            
            # Cari tombol submit dalam modal
            submit_selectors = [
                "#LoginForm #form-login-btnSubmit",
                "#form-login-btnSubmit",
                "#LoginForm button.btn-submit",
                "#LoginForm button[type='button']",
                ".modal #form-login-btnSubmit",
                ".modal button.btn-submit",
                ".modal button[data-loading-text*='Processing']",
                "//div[@id='LoginForm']//button[@id='form-login-btnSubmit']",
                "//div[@id='LoginForm']//button[contains(@class, 'btn-submit')]",
                "//div[@id='LoginForm']//button[contains(text(), 'SUBMIT')]"
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    if selector.startswith("//"):
                        submit_button = modal_wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    else:
                        submit_button = modal_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                
                    if submit_button.is_displayed() and submit_button.is_enabled():
                        logger.info(f"✅ Tombol submit ditemukan dengan selector: {selector}")
                        break
                except:
                    continue
        
            if submit_button:
                logger.info("🚀 Menekan tombol submit...")
                
                # Scroll ke tombol submit dalam modal
                self.driver.execute_script("""
                    arguments[0].scrollIntoView({block: 'center', inline: 'center'});
                    arguments[0].style.border='3px solid red';
                """, submit_button)
                time.sleep(0.3)  # Dikurangi dari 1 ke 0.3
                
                # Coba beberapa metode klik
                success = False
                
                # Method 1: Regular click
                try:
                    submit_button.click()
                    success = True
                    logger.info("✅ Submit berhasil dengan regular click")
                except ElementClickInterceptedException:
                    logger.info("⚠️ Regular click gagal, mencoba JavaScript click...")
                    
                    # Method 2: JavaScript click
                    try:
                        self.driver.execute_script("arguments[0].click();", submit_button)
                        success = True
                        logger.info("✅ Submit berhasil dengan JavaScript click")
                    except Exception as e:
                        logger.warning(f"JavaScript click gagal: {e}")
                        
                        # Method 3: Force click dengan koordinat
                        try:
                            location = submit_button.location_once_scrolled_into_view
                            self.driver.execute_script(f"""
                                var element = arguments[0];
                                var event = new MouseEvent('click', {{
                                    view: window,
                                    bubbles: true,
                                    cancelable: true,
                                    clientX: {location['x']},
                                    clientY: {location['y']}
                                }});
                                element.dispatchEvent(event);
                            """, submit_button)
                            success = True
                            logger.info("✅ Submit berhasil dengan force click")
                        except Exception as e:
                            logger.error(f"Force click gagal: {e}")
            
            if success:
                # Tunggu sebentar untuk proses submit
                time.sleep(5)  # Dikurangi dari 3 ke 2
                logger.info("✅ Form login berhasil disubmit")
                return True
            else:
                logger.error("❌ Semua metode click gagal")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error saat mengisi form login: {e}")
            self.take_screenshot("login_form_error.png")
            return False

    def wait_for_login_popup(self):
        """Menunggu popup login form muncul"""
        logger.info("⏳ Menunggu popup login form muncul...")
        
        try:
            # Tunggu modal LoginForm muncul dan visible
            wait = WebDriverWait(self.driver,0)  # Dikurangi dari 15 ke 10
            
            # Cek berbagai kondisi modal
            modal_conditions = [
                EC.presence_of_element_located((By.ID, "LoginForm")),
                EC.visibility_of_element_located((By.ID, "LoginForm")),
                EC.presence_of_element_located((By.CSS_SELECTOR, ".modal.fade.in[role='dialog']")),
                EC.presence_of_element_located((By.CSS_SELECTOR, ".modal[style*='display: block']"))
            ]
            
            for condition in modal_conditions:
                try:
                    wait.until(condition)
                    logger.info("✅ Modal login form ditemukan dan siap")
                    # time.sleep(1)  # Dikurangi dari 2 ke 1
                    return True
                except TimeoutException:
                    continue
            
            logger.warning("⚠️ Modal login form tidak ditemukan")
            return False
            
        except Exception as e:
            logger.error(f"Error menunggu popup login: {e}")
            return False

    def find_claimable_reward(self):
        """Step 4: Mencari hadiah yang bisa diambil melalui icon star"""
        logger.info("⭐ Step 4: Mencari hadiah yang bisa diambil...")
        
        # Berdasarkan screenshot, hadiah yang bisa diambil memiliki icon star
        claimable_selectors = [
            # Mencari elemen dengan class reward-star atau yang mengandung star
            ".reward-star",
            ".fa-star",
            "//i[contains(@class, 'fa-star')]/..",
            "//div[contains(@class, 'reward-star')]",
            
            # Mencari berdasarkan data atribut dari screenshot
            "[data-period='30'][data-id*='Day-']",
            
            # Mencari div yang clickable untuk claim
            "//div[contains(@class, 'reward-content') and contains(@class, 'dailyClaim')]//div[contains(@class, 'reward-star')]",
            
            # Berdasarkan struktur HTML dari screenshot  
            ".reward-content.dailyClaim .reward-star",
            
            # Alternatif jika menggunakan onclick
            "//div[@onclick and contains(@class, 'reward')]",
            
            # Mencari yang memiliki star dan bisa diklik
            "//div[contains(@class, 'reward-star') and not(contains(@style, 'display: none'))]"
        ]
        
        for selector in claimable_selectors:
            try:
                if selector.startswith("//"):
                    elements = self.driver.find_elements(By.XPATH, selector)
                else:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        logger.info("✅ Hadiah yang bisa diklaim ditemukan!")
                        return element
                        
            except Exception as e:
                logger.debug(f"Error dengan selector {selector}: {e}")
                continue
        
        logger.warning("⚠️ Tidak ada hadiah yang bisa diklaim saat ini")
        return None

    def parse_server_choice(self, server_string):
        """Parse server choice untuk mendapatkan komponen pencarian yang fleksibel"""
        if not server_string:
            return None, None
        
        # Split berdasarkan " - " untuk mendapatkan server dan nama
        parts = server_string.split(" - ")
        
        if len(parts) >= 2:
            server_part = parts[0].strip()  # "Server 39"
            name_part = parts[1].strip()    # "SSINJAA"
            
            # Ekstrak nomor server jika ada
            server_number = None
            if "Server" in server_part:
                try:
                    server_number = server_part.split("Server")[1].strip()
                except:
                    pass
            
            return server_number, name_part
        
        return None, None

    def select_server_from_popup(self):
        """Step 5: Memilih server dari popup dropdown dengan interaksi spinner"""
        logger.info("🌐 Step 5: Memilih server dari popup...")
        
        try:
            # Tunggu popup server muncul
            WebDriverWait(self.driver, 1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select[name='selserver']"))
            )
            
            # Cari dropdown server
            server_dropdown = None
            server_selectors = [
                "select[name='selserver']",
                "select.form-control[name='selserver']",
                "select[data-parsley-required-message*='Must be chosen']"
            ]
            
            for selector in server_selectors:
                try:
                    server_dropdown = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    if server_dropdown.is_displayed():
                        logger.info(f"✅ Dropdown server ditemukan: {selector}")
                        break
                except:
                    continue
    
            if not server_dropdown:
                logger.error("❌ Dropdown server tidak ditemukan")
                self.take_screenshot("server_dropdown_not_found.png")
                return False
            
            # Scroll ke dropdown
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", server_dropdown)
            time.sleep(0.5)
            
            # Parse server choice untuk mendapatkan komponen pencarian
            server_number, server_name = self.parse_server_choice(self.server_choice)
            logger.info(f"🎯 Target server: {self.server_choice}")
            logger.info(f"🔍 Pencarian - Server Number: {server_number}, Server Name: {server_name}")
            
            # METHOD 1: Coba dengan Actions untuk klik dropdown
            try:
                logger.info("🖱️ Method 1: Menggunakan ActionChains untuk klik dropdown")
                actions = ActionChains(self.driver)
                actions.move_to_element(server_dropdown).click().perform()
                time.sleep(0.5)
                
                # Gunakan Select setelah dropdown terbuka
                select = Select(server_dropdown)
                logger.info("📋 Server options tersedia:")
                for option in select.options:
                    logger.info(f"  - Value: {option.get_attribute('value')} | Text: {option.text}")
                
                # Cari dan pilih server yang sesuai
                success = False
                for option in select.options:
                    option_text = option.text
                    
                    # Fleksibel matching berdasarkan komponen yang diparsing
                    match_found = False
                    
                    # Jika ada server number dan name, cek keduanya
                    if server_number and server_name:
                        if (server_number in option_text or f"Server {server_number}" in option_text) and server_name in option_text:
                            match_found = True
                    # Jika hanya ada nama server (fallback)
                    elif server_name and server_name in option_text:
                        match_found = True
                    # Jika cocok persis dengan string asli
                    elif self.server_choice in option_text:
                        match_found = True
                    
                    if match_found:
                        select.select_by_visible_text(option_text)
                        logger.info(f"✅ Server dipilih dengan ActionChains: {option_text}")
                        success = True
                        break
        
                if success:
                    time.sleep(0.5)
                    return True
                
            except Exception as e:
                logger.warning(f"⚠️ Method 1 gagal: {e}")
        
            # METHOD 2: Force set value dengan JavaScript (lebih cepat)
            try:
                logger.info("🖱️ Method 2: Force set value dengan JavaScript")
                
                # Cari value dari option yang sesuai
                select = Select(server_dropdown)
                target_value = None
                target_text = None
                
                for option in select.options:
                    option_text = option.text
                    
                    # Fleksibel matching berdasarkan komponen yang diparsing
                    match_found = False
                    
                    # Jika ada server number dan name, cek keduanya
                    if server_number and server_name:
                        if (server_number in option_text or f"Server {server_number}" in option_text) and server_name in option_text:
                            match_found = True
                    # Jika hanya ada nama server (fallback)
                    elif server_name and server_name in option_text:
                        match_found = True
                    # Jika cocok persis dengan string asli
                    elif self.server_choice in option_text:
                        match_found = True
                    
                    if match_found:
                        target_value = option.get_attribute('value')
                        target_text = option_text
                        break
            
                if target_value:
                    # Set value dengan JavaScript
                    self.driver.execute_script(f"""
                        var select = arguments[0];
                        select.value = '{target_value}';
                        
                        // Trigger events
                        var changeEvent = new Event('change', {{ bubbles: true }});
                        var inputEvent = new Event('input', {{ bubbles: true }});
                        
                        select.dispatchEvent(inputEvent);
                        select.dispatchEvent(changeEvent);
                    """, server_dropdown)
                    
                    logger.info(f"✅ Server dipilih dengan force JavaScript: {target_text}")
                    time.sleep(0.5)
                    return True
                else:
                    logger.error(f"❌ Server '{self.server_choice}' tidak ditemukan dalam dropdown options")
            
            except Exception as e:
                logger.warning(f"⚠️ Method 2 gagal: {e}")
                logger.error("❌ Semua method gagal memilih server")
                self.take_screenshot("server_selection_all_failed.png")
                return False
    
        except Exception as e:
            logger.error(f"❌ Error saat memilih server: {e}")
            self.take_screenshot("server_selection_error.png")
            return False

    def login(self):
        """Proses login lengkap"""
        try:
            logger.info("=== 🚀 MEMULAI PROSES LOGIN NINJA HEROES ===")
            
            # Buka halaman daily event
            logger.info("📱 Membuka halaman daily event...")
            self.driver.get("https://kageherostudio.com/event/?event=daily")
            
            # Tunggu halaman dimuat
            WebDriverWait(self.driver, 0.3).until(  # Dikurangi dari 15 ke 10
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(0.2)  # Dikurangi dari 3 ke 2
            
            # Step 1: Cari tombol login
            login_button = self.find_login_button()
            if login_button:
                login_button.click()
                time.sleep(0.2)  # Dikurangi dari 2 ke 1
                
                # Tunggu popup login muncul
                if self.wait_for_login_popup():
                    # Step 2 & 3: Isi form dan submit
                    if self.fill_login_form():
                        logger.info("✅ Login berhasil!")
                        time.sleep(8)  # Dikurangi dari 3 ke 2
                        return True
                    else:
                        logger.error("❌ Gagal mengisi form login")
                        return False
                else:
                    logger.error("❌ Popup login tidak muncul")
                    return False
            else:
                # Mungkin sudah login, cek status
                logger.info("🔍 Tombol login tidak ditemukan, mungkin sudah login")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error dalam proses login: {e}")
            return False

    def claim_daily_reward(self):
        """Proses claim hadiah harian lengkap"""
        try:
            logger.info("=== 🎁 MEMULAI PROSES CLAIM HADIAH HARIAN ===")
            
            # Step 4: Cari hadiah yang bisa diambil
            claimable_reward = self.find_claimable_reward()
            if not claimable_reward:
                logger.info("ℹ️ Tidak ada hadiah yang bisa diklaim atau sudah diklaim hari ini")
                return "no_claimable_reward"
            
            # Klik hadiah yang bisa diklaim
            logger.info("🎯 Mengklik hadiah yang dapat diklaim...")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", claimable_reward)
            time.sleep(0.5)  # Dikurangi dari 1 ke 0.5
            claimable_reward.click()
            time.sleep(0.2)  # Dikurangi dari 2 ke 1
            
            # Step 5: Pilih server dari popup
            if self.select_server_from_popup():
                # Step 6: Submit form server
                if self.submit_server_form():
                    time.sleep(0.2)  # Dikurangi dari 2 ke 1
                    
                    # Step 7: Handle alert konfirmasi
                    if self.handle_chrome_alert():
                        time.sleep(0.2)  # Dikurangi dari 2 ke 1
                        
                        # Step 8: Cek notifikasi sukses
                        self.check_success_notification()
                        logger.info("🎊 PROSES CLAIM HADIAH SELESAI!")
                        return True
        
            return False
            
        except Exception as e:
            logger.error(f"❌ Error dalam proses claim reward: {e}")
            return False
        
    def submit_server_form(self):
        """Step 6: Submit form server setelah memilih server"""
        logger.info("📤 Step 6: Submit form server...")
        
        try:
            # Tunggu tombol submit muncul dan siap diklik
            submit_selectors = [
                "#form-server-btnSubmit",
                "button#form-server-btnSubmit",
                "button[data-loading-text*='Processing']",
                ".btn.btn-submit",
                "button.btn-submit",
                "//button[@id='form-server-btnSubmit']",
                "//button[contains(@class, 'btn-submit') and text()='SUBMIT']",
                "//button[contains(@data-loading-text, 'Processing')]"
            ]
            
            submit_button = None
            wait = WebDriverWait(self.driver, 10)
            
            for selector in submit_selectors:
                try:
                    if selector.startswith("//"):
                        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    else:
                        submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                
                    if submit_button.is_displayed() and submit_button.is_enabled():
                        logger.info(f"✅ Tombol submit server ditemukan: {selector}")
                        break
                except:
                    continue
        
            if not submit_button:
                logger.error("❌ Tombol submit server tidak ditemukan")
                self.take_screenshot("submit_button_not_found.png")
                return False
            
            # Scroll ke tombol submit
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)
            time.sleep(0.5)
            
            # Highlight tombol untuk debugging
            self.driver.execute_script("arguments[0].style.border='3px solid red';", submit_button)
            time.sleep(0.3)
            
            # Method 1: Regular click
            try:
                logger.info("🖱️ Method 1: Regular click pada tombol submit")
                submit_button.click()
                logger.info("✅ Submit berhasil dengan regular click")
                time.sleep(1)
                return True
                
            except ElementClickInterceptedException:
                logger.info("⚠️ Regular click gagal, mencoba JavaScript click...")
                
                # Method 2: JavaScript click
                try:
                    logger.info("🖱️ Method 2: JavaScript click pada tombol submit")
                    self.driver.execute_script("arguments[0].click();", submit_button)
                    logger.info("✅ Submit berhasil dengan JavaScript click")
                    time.sleep(1)
                    return True
                    
                except Exception as e:
                    logger.warning(f"JavaScript click gagal: {e}")
                    
                    # Method 3: ActionChains click
                    try:
                        logger.info("🖱️ Method 3: ActionChains click pada tombol submit")
                        actions = ActionChains(self.driver)
                        actions.move_to_element(submit_button).click().perform()
                        logger.info("✅ Submit berhasil dengan ActionChains")
                        time.sleep(1)
                        return True
                        
                    except Exception as e:
                        logger.error(f"ActionChains click gagal: {e}")
                        
                        # Method 4: Force submit dengan trigger event
                        try:
                            logger.info("🖱️ Method 4: Force submit dengan event trigger")
                            self.driver.execute_script("""
                                var button = arguments[0];
                                var event = new MouseEvent('click', {
                                    view: window,
                                    bubbles: true,
                                    cancelable: true
                                });
                                button.dispatchEvent(event);
                            """, submit_button)
                            logger.info("✅ Submit berhasil dengan force event")
                            time.sleep(1)
                            return True
                        
                        except Exception as e:
                            logger.error(f"Force event gagal: {e}")
        
            logger.error("❌ Semua metode submit gagal")
            self.take_screenshot("submit_all_methods_failed.png")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error saat submit form server: {e}")
            self.take_screenshot("submit_server_error.png")
            return False

    def handle_chrome_alert(self):
        """Step 7: Handle alert konfirmasi setelah submit"""
        logger.info("🔔 Step 7: Menangani alert konfirmasi...")
        
        try:
            # Tunggu alert muncul
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.alert_is_present())
            
            # Handle alert
            alert = Alert(self.driver)
            alert_text = alert.text
            logger.info(f"📋 Alert text: {alert_text}")
            
            # Accept alert (klik OK)
            alert.accept()
            logger.info("✅ Alert berhasil di-accept")
            return True
            
        except TimeoutException:
            logger.info("ℹ️ Tidak ada alert yang muncul")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saat handle alert: {e}")
            return False

    def check_success_notification(self):
        """Step 8: Cek notifikasi sukses claim reward"""
        logger.info("🎉 Step 8: Mengecek notifikasi sukses...")
        
        try:
            # Selectors untuk notifikasi sukses
            success_selectors = [
                ".alert-success",
                ".notification-success", 
                ".success-message",
                ".toast-success",
                "//div[contains(@class, 'alert') and contains(@class, 'success')]",
                "//div[contains(text(), 'success') or contains(text(), 'Success')]",
                "//div[contains(text(), 'berhasil') or contains(text(), 'Berhasil')]",
                "//div[contains(text(), 'claimed') or contains(text(), 'Claimed')]"
            ]
            
            for selector in success_selectors:
                try:
                    if selector.startswith("//"):
                        element = WebDriverWait(self.driver, 0.2).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                    else:
                        element = WebDriverWait(self.driver, 0.2).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                
                    if element.is_displayed():
                        success_text = element.text
                        logger.info(f"✅ Notifikasi sukses ditemukan: {success_text}")
                        return True
                        
                except TimeoutException:
                    continue
        
            logger.info("ℹ️ Tidak ada notifikasi sukses yang terdeteksi, tapi submit telah dilakukan")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saat cek notifikasi: {e}")
            return True  # Return True karena ini bukan critical error

    def take_screenshot(self, filename="screenshot.png"):
        """Ambil screenshot untuk debugging dengan auto-indexing"""
        try:
            # Pisahkan nama file dan ekstensi
            name, ext = os.path.splitext(filename)
            
            # Cek apakah file sudah ada, jika ya tambahkan index
            counter = 1
            new_filename = filename
            
            while os.path.exists(new_filename):
                new_filename = f"{name}_{counter}{ext}"
                counter += 1
            
            self.driver.save_screenshot(new_filename)
            logger.info(f"📸 Screenshot disimpan: {new_filename}")
            return new_filename
            
        except Exception as e:
            logger.error(f"❌ Error saat mengambil screenshot: {e}")
            return None

    def close_driver(self):
        """Tutup driver"""
        if self.driver:
            self.driver.quit()
            logger.info("🔚 Driver ditutup")

    def run(self):
        """Jalankan bot utama"""
        try:
            self.setup_driver()
            
            # Login terlebih dahulu
            if self.login():
                time.sleep(0.2)  # Dikurangi dari 2 ke 1
                
                # Claim daily reward
                claim_result = self.claim_daily_reward()
                if claim_result == "no_claimable_reward":
                    logger.info("ℹ️ Tidak ada hadiah yang bisa diklaim hari ini")
                    self.take_screenshot("no_reward.png")
                    return True
                elif claim_result == True:
                    # Sukses claim reward
                    logger.info("✅ Daily reward berhasil diklaim!")
                    logger.info("🎉 BOT BERHASIL MENJALANKAN SEMUA TUGAS!")
                    self.take_screenshot("success.png")
                    return True
                else:
                    logger.error("❌ Gagal claim daily reward")
                    self.take_screenshot("error_claim.png")
                    return False
            else:
                logger.error("❌ Login gagal")
                self.take_screenshot("error_login.png")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error dalam menjalankan bot: {e}")
            self.take_screenshot("error_general.png")
            return False
        finally:
            time.sleep(0.5)  # Beri waktu untuk melihat hasil
            self.close_driver()

# Cara penggunaan
if __name__ == "__main__":
    load_dotenv("config.env")

    EMAIL = os.getenv("EMAIL")
    PASSWORD = os.getenv("PASSWORD")
    SERVER = os.getenv("SERVER")

    # ✅ Validasi environment variables
    if not EMAIL or not PASSWORD or not SERVER:
        print("❌ Error: EMAIL, PASSWORD, dan SERVER harus diset di config.env")
        print("📝 Copy config.env.example menjadi config.env dan isi dengan data Anda")
        exit(1)

    # Cek apakah masih menggunakan nilai default/example
    if EMAIL == "your_email@example.com":
        print("❌ Error: Silakan ganti EMAIL di config.env dengan email asli Anda")
        exit(1)

    bot = NinjaHeroesBot(
        email=EMAIL, 
        password=PASSWORD, 
        server_choice=SERVER,
        headless=False
    )

    success = bot.run()

    if success:
        print("✅ Bot berhasil dijalankan!")
    else:
        print("❌ Bot gagal dijalankan, periksa log untuk detail error")
