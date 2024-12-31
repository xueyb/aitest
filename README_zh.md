# ShowUI-2B 自动化测试工具

这是一个基于 **Multimodal-Large-Model**(showlab/ShowUI-2B、Qwen/Qwen2-VL-2B-Instruct) 的自动化测试工具, 可以通过自然语言描述来定位 UI 元素, 执行操作和验证结果。

## 功能特点

- 支持通过自然语言描述定位 UI 元素
- 支持本地和远程模型部署
- 支持 Android 和 iOS 设备
- 支持 YAML 格式的测试用例编写
- 提供可视化的点击位置标记
- 提供测试过程回放

## 安装
```
./install.sh
```

## 配置
config.yml 是配置文件，用于配置定位模型和验证模型。

## 测试用例
测试用例放在 `cases` 目录下，用例文件名以 `test_` 开头，用例文件名以 `.yml` 结尾。

## 可执行程序
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

## 环境搭建
### appium server
启动appium server, 并修改config.yml中的:
```
appium-server-host: {appium-server-host}
```

### 多模态大语言模型 - ShowUI-2B (支持本地和远程模式)
部署 showlab/ShowUI-2B, 并修改 config.yml:
```
# 本地模式. 你的机器需要有更强的性能, 否则会很慢.
locate-model-type: local

# 远程模式
locate-model-type: remote  
locate-model-host: {locate-model-host}
```

### 多模态大语言模型 - Qwen2-VL-2B-Instruct (支持本地和远程模式)
部署 Qwen/Qwen2-VL-2B-Instruct, 并修改 config.yml:
```
# 本地模式. 你的机器需要有更强的性能, 否则会很慢.
validate-model-type: local

# 远程模式
validate-model-type: remote  
validate-model-host: {validate-model-host}
```

### 设备 (支持 Android 和 iOS)
``` 
# Android
device-type: android
app-package: {app-package}
app-activity: {app-activity}

# iOS todo
device-type: ios
```



