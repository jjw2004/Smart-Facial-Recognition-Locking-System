import time
import threading
import requests
import os
import cv2  # OpenCV for USB webcam
from grove.gpio import GPIO
from grove.grove_relay import GroveRelay
from grove.adc import ADC
from grove.display.jhd1802 import JHD1802

# ───── CONFIG ─────
PHOTO_DIR = "/home/joey/face-stuff"
BUTTON_PIN = 5
BUZZER_PIN = 16
RELAY_PIN = 18
LIGHT_CHANNEL = 2
LIGHT_THRESHOLD = 100
SERVER_URL = 'http://192.168.1.14:5002/verify'

# ───── GPIO ─────
button = GPIO(BUTTON_PIN)
button.dir(GPIO.IN)

buzzer = GPIO(BUZZER_PIN)
buzzer.dir(GPIO.OUT)

relay = GroveRelay(RELAY_PIN)

# ───── LCD SETUP ─────
lcd = JHD1802()

def lcd_update_top(line=""):
    lcd.setCursor(0, 0)
    lcd.write(line[:16].ljust(16))

def lcd_update_bottom(line=""):
    lcd.setCursor(1, 0)
    lcd.write(line[:16].ljust(16))

# ───── LIGHT SENSOR ─────
class GroveLightSensor:
    def __init__(self, channel):
        self.channel = channel
        self.adc = ADC(address=0x08)

    @property
    def light(self):
        return self.adc.read(self.channel)

light_sensor = GroveLightSensor(LIGHT_CHANNEL)

# ───── BUZZER ─────
def happy_beep():
    for _ in range(2):
        buzzer.write(1)
        time.sleep(0.1)
        buzzer.write(0)
        time.sleep(0.1)

def sad_beep():
    buzzer.write(1)
    time.sleep(0.5)
    buzzer.write(0)

# ───── RELAY ─────
def unlock_door():
    print("Unlocking door")
    relay.on()
    time.sleep(10)
    relay.off()
    print("Door locked")

# ───── LIGHT MONITOR THREAD ─────
def monitor_light():
    global current_status_line
    while True:
        light_val = light_sensor.light
        if light_val < LIGHT_THRESHOLD:
            print(f"[⚠️ Light Warning] Low ambient light ({light_val})")
            lcd_update_top(current_status_line)
            lcd_update_bottom("Turn on light")
        else:
            print(f"[✅ Light OK] Light level: {light_val}")
            lcd_update_top(current_status_line)
            lcd_update_bottom("Light OK")
        time.sleep(5)

# ───── FACE VERIFY ─────
current_status_line = "Press button"

def take_picture_and_send():
    global current_status_line

    image_path = f"{PHOTO_DIR}/image1.jpg"

    current_status_line = "Taking picture"
    lcd_update_top(current_status_line)
    print(current_status_line)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open webcam")
        current_status_line = "Camera error"
        lcd_update_top(current_status_line)
        sad_beep()
        return

    time.sleep(2)  # allow camera to adjust
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("❌ Failed to capture image")
        current_status_line = "Capture failed"
        lcd_update_top(current_status_line)
        sad_beep()
        return

    cv2.imwrite(image_path, frame)
    print(f"Image saved to {image_path}")
    time.sleep(0.5)

    if os.path.exists(image_path) and os.path.getsize(image_path) > 0:
        with open(image_path, 'rb') as img_file:
            files = {'image1': ('image1.jpg', img_file, 'image/jpeg')}
            try:
                response = requests.post(SERVER_URL, files=files)
                print(f"Status Code: {response.status_code}")
                response_json = response.json()
                print(f"Response: {response_json}")

                user = response_json.get('user', 'UNKNOWN')
                verified = response_json.get('verified', False)

                if verified and user != "UNKNOWN":
                    msg = f"Welcome: {user}"[:16]
                    print(f"✅ {msg}")
                    current_status_line = msg
                    lcd_update_top(current_status_line)
                    happy_beep()
                    unlock_door()

                    time.sleep(5)
                    current_status_line = "Press button"
                    lcd_update_top(current_status_line)

                else:
                    msg = "Not verified"
                    print(f"❌ {msg}")
                    current_status_line = msg
                    lcd_update_top(current_status_line)
                    sad_beep()

            except requests.exceptions.RequestException as e:
                print(f"Error sending POST: {e}")
                current_status_line = "Network error"
                lcd_update_top(current_status_line)
                sad_beep()
    else:
        print("Error: image missing or empty.")
        current_status_line = "Image error"
        lcd_update_top(current_status_line)
        sad_beep()

# ───── MAIN LOOP ─────
try:
    lcd_update_top("System starting")
    lcd_update_bottom("Please wait")
    time.sleep(2)
    current_status_line = "Press button"
    lcd_update_top(current_status_line)
    lcd_update_bottom("")

    threading.Thread(target=monitor_light, daemon=True).start()

    print("Ready. Waiting for button press...")
    while True:
        if button.read() == 1:
            current_status_line = "Taking picture"
            lcd_update_top(current_status_line)
            print("Button pressed")
            take_picture_and_send()
            time.sleep(1)  # Debounce
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting...")
    relay.off()
    lcd_update_top("Goodbye!")
    lcd_update_bottom("")
