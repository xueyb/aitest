# ShowUI-2B Automation Testing Tool

(If you have any questions, please send an email to: `olkingbing@gmail.com`)

This is an **Automation-Testing-Tool** based on **Multimodal-Large-Model**(showlab/ShowUI-2B、Qwen/Qwen2-VL-2B-Instruct), which can locate UI elements, execute actions and validate results through natural language description.

## 1. Features

- Support locating UI elements through natural language description
- Support local and remote model deployment
- Support Android and iOS devices
- Support YAML format test case writing
- Provide visual click position marking
- Provide test process playback

## 2. Installation
```
./install.sh
```

## 3. Configuration
`config.yml` is the configuration file, used to configure the locate model and validate model.

## 4. Test Cases
Test cases are placed in the `cases` directory, with the test case file name starting with `test_` and ending with `.yml`.

## 5. Executable Program
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

## 6. Environment Setup
### 6.1 Appium Server
start appium server, and modify `config.yml`中的:
```
appium-server-host: http://127.0.0.1:4723
```

### 6.2 Deploy MLLMs - Local Mode (Not Recommend)
If your machine has a strong performance, you can run the project in local mode. modify `config.yml` as follows(otherwise, please deploy MLLMs in remote mode):
```
locate-model-type: local
validate-model-type: local
```

### 6.3 Deploy MLLMs - Remote Mode (Recommend)
except local mode, you can also run the project in remote mode. you need to prepare a GPU server, and do the following:

#### 6.3.1 Install vllm
```
pip install vllm
```

#### 6.3.2 Deploy MLLMs - ShowUI-2B
1. Deploy showlab/ShowUI-2B
```
vllm serve showlab/ShowUI-2B --port 8001
```
2. Modify `config.yml`:
```
locate-model-type: remote  
locate-model-host: http://{ip}:8001
```

#### 6.3.3 Deploy MLLMs - Qwen2-VL-2B-Instruct
1. Deploy Qwen/Qwen2-VL-2B-Instruct
```
vllm serve Qwen/Qwen2-VL-2B-Instruct --port 8002
```
2. Modify `config.yml`:
```
validate-model-type: remote  
validate-model-host: http://{ip}:8002
```

### 6.4 Device (support Android and iOS)
``` 
# Android
device-type: android
app-package: {app-package}
app-activity: {app-activity}

# iOS todo
device-type: ios
```



