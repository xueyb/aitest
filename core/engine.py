import os
import shutil
import time
import yaml
import config
import logging
import argparse

from mobile.client import AndroidClient, IOSClient
from models.locate import LocalLocate, RemoteLocate
from models.validate import LocalValidate, RemoteValidate

class Engine:
    def __init__(self, run_path):
        self.client = None
        self.locate = None
        self.validate = None
        self.run_path=run_path

        parser = argparse.ArgumentParser(description='Automated Testing based on Appium and AI', formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('--config-file', type=str, metavar='', help='\nConfiguration file path, default: ./config.yml')
        parser.add_argument('--case-path', type=str, metavar='', help='\nCase directory path, default: ./cases/')
        parser.add_argument('--appium-server-host', type=str, metavar='', help='\nAppium server host, default: http://127.0.0.1:4723')
        parser.add_argument('--locate-model-type', type=str, metavar='', help='\nLocate model type, support: local, remote')
        parser.add_argument('--locate-model-host', type=str, metavar='', help='\nLocate model remote host')
        parser.add_argument('--validate-model-type', type=str, metavar='', help='\nValidate model type, support: local, remote')
        parser.add_argument('--validate-model-host', type=str, metavar='', help='\nValidate model remote host')
        parser.add_argument('--device-type', type=str, metavar='', help='\nDevice type, support: android, ios')
        parser.add_argument('--app-package', type=str, metavar='', help='\nApplication package name')
        parser.add_argument('--app-activity', type=str, metavar='', help='\nApplication activity name')
        args = parser.parse_args()

        if args.config_file is not None:
            if os.path.isabs(args.config_file):
                self.conf = config.load_config(args.config_file)
            else:
                self.conf = config.load_config(os.path.join(self.run_path, args.config_file))
        else:
            self.conf = config.load_config(os.path.join(self.run_path, "config.yml"))

        if args.case_path is not None:
            self.case_path = args.case_path
        else:
            self.case_path = os.path.join(self.run_path, "cases")  

        if args.device_type is not None:
            self.conf.device_type = args.device_type
        if args.app_package is not None:
            self.conf.app_package = args.app_package
        if args.app_activity is not None:
            self.conf.app_activity = args.app_activity


    def start(self):
        logging.info(f"the running path is : {self.run_path}")
        if self.conf.device_type == "android":
            self.client = AndroidClient(self.run_path, self.conf)
        elif self.conf.device_type == "ios":
            self.client = IOSClient(self.run_path, self.conf)
        else:
            logging.error(f"device type is not supported: {self.conf.device_type}")
            exit(1)
        self.conf.device_width = self.client.device_width
        self.conf.device_height = self.client.device_height
        
        # initialize locate model
        if self.conf.locate_model_type == "local":
            self.locate = LocalLocate(self.conf, self.run_path)
            logging.info("locate model initialized in Local mode")
        elif self.conf.locate_model_type == "remote":
            self.locate = RemoteLocate(self.conf, self.run_path)
            logging.info("locate model initialized in Remote mode")
        else:
            logging.error(f"locate model mode is not supported: {self.conf.locate_model_type}")
            exit(1)

        # initialize validate model
        if self.conf.validate_model_type == "local":
            self.validate = LocalValidate(self.conf, self.run_path)
            logging.info("validate model initialized in Local mode")
        elif self.conf.validate_model_type == "remote":
            self.validate = RemoteValidate(self.conf, self.run_path)
            logging.info("validate model initialized in Remote mode")
        else:
            logging.error(f"validate model mode is not supported: {self.conf.validate_model_type}")
            exit(1)
        self._core()


    def _core(self):
        if os.path.isfile(self.case_path):
            if self.case_path.startswith("test_") and self.case_path.endswith(".yml"):
                logging.info(f"execute case: {self.case_path}")
                self._run(self.case_path)
            else:
                logging.error(f"case file is not a yml file: {self.case_path}")
        else:
            logging.info(f"execute all cases in {self.case_path}")
            # clear existing execution records, including screencaps and screencaps_validation
            screencaps_path = os.path.join(self.run_path, "records/screencaps")
            if os.path.exists(screencaps_path):
                shutil.rmtree(screencaps_path)
            screenrecords_path = os.path.join(self.run_path, "records/screenrecords")
            if os.path.exists(screenrecords_path):
                shutil.rmtree(screenrecords_path)

            for file in os.listdir(self.case_path):
                if file.startswith("test_") and file.endswith(".yml"):
                    logging.info(f"execute case: {file}")
                    self._run(os.path.join(self.case_path, file))
                else:
                    logging.warning(f"case file is not start with test_ or not a yml file: {file}")

    def _run(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            cases_data = yaml.safe_load(f)["cases"]

        cases = []
        for case_data in cases_data:
            case = Case(
                name=case_data["case"]["name"],
                steps=case_data["case"]["steps"]
            )
        cases.append(case)

        for case in cases:
            self.client.start_screenrecord()
            logging.info(f"- execute case: {case.name}")
            for step in case.steps:
                time.sleep(2)
                logging.info(f"-- execute step: {step}")
                if step.action == "click":
                    self.client.take_screenshot(step.element)
                    coordinate = self.locate.locate_pixel(step.element)
                    self.client.touch_at_coordinate(coordinate)
                    if step.validation:
                        time.sleep(2)
                        self.client.take_screenshot(f"{step.element}_validation")
                        is_ok = self.validate.validate(step.element, step.validation)
                        if not is_ok:
                            logging.error(f"case 【{case.name}】 failed at step 【{step}】")
                            break
                elif step.action == "input":
                    self.client.take_screenshot(step.element)
                    coordinate = self.locate.locate_pixel(step.element)
                    self.client.touch_at_coordinate(coordinate)
                    self.client.send_keys(coordinate, step.text)
                    if step.validation:
                        time.sleep(2)
                        self.client.take_screenshot(f"{step.element}_validation")
                        is_ok = self.validate.validate(step.element, step.validation)
                        if not is_ok:
                            logging.error(f"case 【{case.name}】 failed at step 【{step}】")
                            break
                elif step.action == "swipe":
                    self.client.take_screenshot(step.from_element)
                    from_coordinate = self.locate.locate_pixel(step.from_element)
                    self.client.take_screenshot(step.to_element)
                    to_coordinate = self.locate.locate_pixel(step.to_element)
                    self.client.swipe_from_coordinate(from_coordinate, to_coordinate)
                    if step.validation:
                        time.sleep(2)
                        self.client.take_screenshot(f"{step.to_element}_validation")
                        is_ok = self.validate.validate(step.to_element, step.validation)
                        if not is_ok:
                            logging.error(f"case 【{case.name}】 failed at step 【{step}】")
                            break
                else:
                    logging.info(f"unknown action: {step.action}")
            self.client.stop_screenrecord(case.name)

class Step:
    def __init__(self, element, action, text=None, from_element=None, to_element=None, validation=None):
        self.element = element
        self.action = action
        self.text = text
        self.from_element = from_element
        self.to_element = to_element
        self.validation = validation

    def __str__(self):
        return f"Step(element={self.element}, action={self.action}, text={self.text}, from_element={self.from_element}, to_element={self.to_element}, validation={self.validation})"

class Case:
    def __init__(self, name, steps):
        self.name = name
        self.steps = [Step(
            element=step.get("element"),
            action=step["action"],
            text=step.get("text"),
            from_element=step.get("from_element"),
            to_element=step.get("to_element"),
            validation=step.get("validation")
        ) for step in steps]

    def __str__(self):
        return f"Case(name={self.name}, steps={self.steps})"
