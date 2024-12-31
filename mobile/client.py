import os
import time
import config
import logging
from appium.options.android import UiAutomator2Options
from appium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

# defind Android and iOS enums
class DevicePlatform:
    ANDROID = "Android"
    IOS = "iOS"

class Coordinate():
    def __init__(self, x_pixel, y_pixel):
        self.x_pixel = x_pixel
        self.y_pixel = y_pixel


# define the base class for all clients
class Client:
    def __init__(self, run_path: str, driver: webdriver.Remote):
        self.run_path = run_path
        self.driver = driver
        self.device_width = driver.get_window_size()['width']
        self.device_height = driver.get_window_size()['height']
        logging.info(f"device width: {self.device_width}, device height: {self.device_height}")

    def take_screenshot(self, image_name, file_format='png'):
        try:
            img_folder = os.path.join(self.run_path, 'records/screencaps')

            if not os.path.exists(img_folder):
                os.makedirs(img_folder)

            screen_save_path = os.path.join(img_folder, f"{image_name}.{file_format}")
            self.driver.get_screenshot_as_file(os.path.abspath(screen_save_path))
            if os.path.exists(screen_save_path):
                logging.info(f"screenshot saved successfully, path: {os.path.abspath(screen_save_path)}")
                return True
            else:
                logging.info("screenshot saved failed")
                return False
        except Exception as e:
            logging.info(f"screenshot error: {str(e)}")
            return False

    def start_screenrecord(self):
        try:
            self.driver.start_recording_screen()

            time.sleep(3)
            return True
        except Exception as e:
            logging.info(f"start screenrecord error: {str(e)}")
            return False

    def stop_screenrecord(self, case_name, file_format='mp4'):
        try:
            video_folder = os.path.join(self.run_path, 'records/screenrecords')

            if not os.path.exists(video_folder):
                os.makedirs(video_folder)

            screen_save_path = os.path.join(video_folder, f"{case_name}.{file_format}")

            screen_recording = self.driver.stop_recording_screen()

            with open(screen_save_path, "wb") as file:
                file.write(screen_recording)

            if os.path.exists(screen_save_path):
                logging.info(f"screenrecord saved successfully, path: {screen_save_path}")
                return True
            else:
                logging.info("screenrecord saved failed")
                return False
        except Exception as e:
            logging.info(f"stop screenrecord error: {str(e)}")
            return False

    def touch_at_coordinate(self, coordinate: Coordinate):
        try:
            self.driver.tap([(coordinate.x_pixel, coordinate.y_pixel)])
            return True
        except Exception as e:
            logging.info(f"touch at coordinate failed: {str(e)}")
            return False

    def swipe_from_coordinate(self, from_coordinate: Coordinate, to_coordinate: Coordinate, duration=500):
        try:
            self.driver.press(x=from_coordinate.x_pixel, y=from_coordinate.y_pixel).wait(duration).move_to(x=to_coordinate.x_pixel, y=to_coordinate.y_pixel).release().perform()
            return True
        except Exception as e:
            logging.info(f"swipe from coordinate failed: {str(e)}")
            return False

    def send_keys(self, coordinate: Coordinate, content):
        try:
            self.driver.tap([(coordinate.x_pixel, coordinate.y_pixel)])
            time.sleep(1)

            if content is None:
                logging.info("text content is empty, skip input")
                return True

            ActionChains(self.driver).send_keys(content).perform()
            return True

        except Exception as e:
            logging.info(f"send keys failed: {str(e)}")
            return False

    def quit(self):
        self.driver.quit()

class AndroidClient(Client):
    def __init__(self, run_path: str, config: config.Config, dontStopAppOnReset: bool = False):
        logging.info(f"initialize Android client: app_package: {config.app_package}, app_activity: {config.app_activity}")
        caps = {
            "platformName": DevicePlatform.ANDROID,
            "appPackage": config.app_package,
            "appActivity": config.app_activity,
            "noReset": True,
            "automationName": "UiAutomator2",
            "newCommandTimeout": 3600,
            "sessionOverride": True,
            "dontStopAppOnReset": dontStopAppOnReset
        }

        try:
            driver = webdriver.Remote(
                command_executor=config.appium_server_host,
                options=UiAutomator2Options().load_capabilities(caps)
            )
            super().__init__(run_path, driver)
            logging.info("initialize android client success")
        except Exception as e:
            logging.info(f"init Android client failed: {str(e)}")
            raise


class IOSClient(Client):
    def __init__(self, run_path: str, config: config.Config):
        # confing device capabilities
        desired_caps = {
        }
        try:
            driver = webdriver.Remote(config.appium_server_host, desired_caps)
            super().__init__(run_path, driver)
            logging.info("initialize iOS client success")
        except Exception as e:
            logging.info(f"init iOS client failed: {str(e)}")
            raise
