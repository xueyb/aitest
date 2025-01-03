# ShowUI-2B 自动化测试工具
（如有任何疑问，发送邮件至：`olkingbing@gmail.com`）

这是一个基于 **Multimodal-Large-Model**(showlab/ShowUI-2B、Qwen/Qwen2-VL-2B-Instruct) 的自动化测试工具, 可以通过自然语言描述来定位 UI 元素, 执行操作和验证结果。

## 1. 功能特点

- 支持通过自然语言描述定位 UI 元素
- 支持本地和远程模型部署
- 支持 Android 和 iOS 设备
- 支持 YAML 格式的测试用例编写
- 提供可视化的点击位置标记
- 提供测试过程回放

## 2. 安装
```
./install.sh
```

## 3. 配置
`config.yml` 是配置文件，用于配置定位模型和验证模型。

## 4. 测试用例
测试用例放在 `cases` 目录下，用例文件名以 `test_` 开头，用例文件名以 `.yml` 结尾。

## 5. 可执行程序
```
# 直接运行
aitest

# 查看帮助
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

## 6. 环境搭建
### 6.1 Appium Server
启动appium server, 并修改`config.yml`中的:
```
appium-server-host: http://127.0.0.1:4723
```

### 6.2 部署MLLMs-本地模式(不推荐)
如果本地开发机器性能足够好，则可以local模式启动项目, 按如下修改`config.yml`即可（否则建议在服务器部署MLLMs后，以remote模式启动项目）:
```
locate-model-type: local
validate-model-type: local
```

### 6.3 部署MLLMs-远程模式（推荐）
除了local模式, 还可以remote模式启动项目, 需准备一台性能足够好的GPU服务器, 并进行如下操作:
#### 6.3.1 安装vllm
```
pip install vllm
```

#### 6.3.2 部署多模态大语言模型 - ShowUI-2B
1. 部署 showlab/ShowUI-2B
```
vllm serve showlab/ShowUI-2B --port 8001
```

2. 修改 config.yml:
```
# 远程模式
locate-model-type: remote  
locate-model-host: http://{ip}:8001
```

#### 6.3.3 部署多模态大语言模型 - Qwen2-VL-2B-Instruct
1. 部署 Qwen/Qwen2-VL-2B-Instruct
```
vllm serve Qwen/Qwen2-VL-2B-Instruct --port 8002
```

2. 修改 config.yml:
```
# 远程模式
validate-model-type: remote  
validate-model-host: http://{ip}:8002
```

### 6.4 设备 (支持 Android 和 iOS)
``` 
# Android
device-type: android
app-package: {app-package}
app-activity: {app-activity}

# iOS todo
device-type: ios
```



