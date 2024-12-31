#!/bin/bash
# check if brew is installed
if ! brew -v >/dev/null 2>&1; then
    printf "brew is not installed, starting to install brew\n"
    if ! /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" >/dev/null 2>&1; then
        printf "Failed to install brew, please check if the installation process has errors\n"
        exit 1
    fi
fi

# check if npm is installed
if ! npm -v >/dev/null 2>&1; then
    printf "npm is not installed, starting to install npm\n"
    if ! brew install npm >/dev/null 2>&1; then
        printf "Failed to install npm, please check if the installation process has errors\n"
        exit 1
    fi
fi

appium_version=$(appium --version | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+')
if [[ -z $appium_version ]]; then
    printf "can not get appium version, starting to install appium@2.13.1\n"
    if ! npm install -g appium@2.13.1 >/dev/null 2>&1; then
        printf "Appium installation failed, the possible reasons are:\n"
        printf " - network problem, check if the network is normal\n"
        printf " - permission problem, ensure you have enough permissions to install globally\n"
        printf " - npm repository problem, try to change npm source and install again\n"
        exit 1
    fi
else
    major=$(echo $appium_version | cut -d. -f1)
    minor=$(echo $appium_version | cut -d. -f2)
    patch=$(echo $appium_version | cut -d. -f3)
    printf "current appium version is $major.$minor.$patch\n"
    if ((major < 2 || (major == 2 && minor < 13) || (major == 2 && minor == 13 && patch < 1))); then
        printf "current appium version is less than 2.13.1, starting to upgrade\n"
        if !npm install -g appium@2.13.1 >/dev/null 2>&1; then
            printf "Appium upgrade failed, the possible reasons are:\n"
            printf " - network problem, check if the network is normal\n"
            printf " - permission problem, ensure you have enough permissions to install globally\n"
            printf " - npm repository problem, try to change npm source and install again\n"
            exit 1
        fi
    else
        printf "Appium is 2.13.1 or later, no need to upgrade\n"
    fi
fi

if ! brew list anaconda >/dev/null 2>&1; then
    printf "Anaconda is not installed, starting to install anaconda\n"
    brew install anaconda
else
    printf "Anaconda is already installed\n"
fi

if ! echo $PATH | grep -q "/usr/local/anaconda3/bin"; then
    echo -e "\nexport PATH=/usr/local/anaconda3/bin:\$PATH" >>~/.bash_profile
    source ~/.bash_profile
fi

if ! conda --version >/dev/null 2>&1; then
    printf "Conda install failed, please check if the installation process has errors\n"
    exit 1
fi
printf "Conda is installed successfully\n"

# check if conda environment aitest is already created
if ! conda env list | awk '{print $1}' | grep -q "^aitest$"; then
    printf "Conda environment aitest is not created, starting to create\n"
    conda create --name aitest python=3.12 -y
else
    printf "Conda environment aitest is already created\n"
fi

#  check if conda environment aitest is activated
if [[ $CONDA_DEFAULT_ENV != "aitest" ]]; then
    printf "Conda environment aitest is not activated, starting to activate\n"
    conda activate aitest >/dev/null 2>&1
    if [[ $CONDA_DEFAULT_ENV != "aitest" ]]; then
        printf "Failed to activate conda environment aitest, please manually check the activation status\n"
        exit 1
    else
        printf "Successfully activated conda environment aitest\n"
    fi
else
    printf "Conda environment aitest is already activated\n"
fi

ping -c 2 -W 3 huggingface.co >/dev/null 2>&1
if [ $? -eq 0 ]; then
    printf "Huggingface mirror address is not needed\n"
else
    printf "Huggingface mirror address is needed\n"
    if [[ -z "${HF_ENDPOINT}" ]]; then
        echo "export HF_ENDPOINT=\"https://hf-mirror.com\"" >>~/.bash_profile
        source ~/.bash_profile
        printf "Successfully set Huggingface mirror address, current mirror address is https://hf-mirror.com\n"
    else
        printf "Huggingface mirror address is already set, no need to add it again\n"
    fi
fi

ping -c 2 -W 3 pypi.org >/dev/null 2>&1
if [ $? -eq 0 ]; then
    printf "Pypi mirror address is not needed\n"
    pip3 install -r requirements.txt
else
    printf "Pypi mirror address is needed\n"
    pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
fi

if [ $? -ne 0 ]; then
    printf "Failed to install requirements, please check if the installation process has errors\n"
    exit 1
fi

printf "Successfully installed all dependencies\n"

VIRTUAL_ENV=$(python -c "import sys; print(sys.prefix)")

# pyinstaller --onefile --path "${VIRTUAL_ENV}/lib/python3.12/site-packages" --add-data "${VIRTUAL_ENV}/lib/python3.12/site-packages/gradio_client/types.json:gradio_client" --exclude-module "showui-2b" --exclude-module "qwen2-vl" --name aitest aitest.py
pyinstaller --onefile --path "${VIRTUAL_ENV}/lib/python3.12/site-packages" --exclude-module "showui-2b" --exclude-module "qwen2-vl" --name aitest aitest.py

mv dist/aitest aitest && chmod +x aitest

rm -rf build dist aitest.spec

printf "Successfully built aitest\n"
printf "$(pwd)/aitest is the executable file\n"
printf "You can run it with the following command:\n"
printf "  ./aitest\n"
