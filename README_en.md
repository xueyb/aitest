# ShowUI-2B Automation Testing Tool

This is an **Automation-Testing-Tool** based on **Multimodal-Large-Model**(showlab/ShowUI-2B、Qwen/Qwen2-VL-2B-Instruct), which can locate UI elements, execute actions and validate results through natural language description.

## Features

- Support locating UI elements through natural language description
- Support local and remote model deployment
- Support Android and iOS devices
- Support YAML format test case writing
- Provide visual click position marking
- Provide test process playback

## Installation
```
./install.sh
```

## Configuration
config.yml is the configuration file, used to configure the locate model and validate model.

## Test Cases
Test cases are placed in the `cases` directory, with the test case file name starting with `test_` and ending with `.yml`.

## Executable Program
```
# Run directly
aitest

# View help
aitest [-h] [--config-file] [--case-path] [--appium-server-host] [--locate-model-type] [--locate-model-host] [--validate-model-type]
                 [--validate-model-host] [--device-type] [--app-package] [--app-activity]

Automated Testing based on Appium and AI

options:
  -h, --help            show this help message and exit
  --config-file         
                        Configuration file path, default: ./config.yml
  --case-path           
                        Case directory path, default: ./cases/
  --appium-server-host 
                        
                        Appium server host, default: http://127.0.0.1:4723
  --locate-model-type   
                        Locate model type, support: local, remote
  --locate-model-host   
                        Locate model remote host
  --validate-model-type 
                        
                        Validate model type, support: local, remote
  --validate-model-host 
                        
                        Validate model remote host
  --device-type         
                        Device type, support: android, ios
  --app-package         
                        Application package name
  --app-activity        
                        Application activity name
```

## Environment Setup
### appium server
启动appium server, 并修改config.yml中的:
```
appium-server-host: {appium-server-host}
```

### Multi-modal large language model - ShowUI-2B (support remote and local mode)
Deploy showlab/ShowUI-2B, and modify config.yml:
```
# local mode. your machine need have a stronger performance, otherwise it will be very slow.
locate-model-type: local

# remote mode
locate-model-type: remote  
locate-model-host: {locate-model-host}
```

### Multi-modal large language model - Qwen2-VL-2B-Instruct (support remote and local mode)
Deploy Qwen/Qwen2-VL-2B-Instruct, and modify config.yml:
```
# local mode. your machine need have a stronger performance, otherwise it will be very slow.
validate-model-type: local

# remote mode 
validate-model-type: remote  
validate-model-host: {validate-model-host}
```

### Device (support Android and iOS)
``` 
# Android
device-type: android
app-package: {app-package}
app-activity: {app-activity}

# iOS todo
device-type: ios
```



