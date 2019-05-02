# azurlane-auto
**ALAuto** is an Azur Lane automation tool based on [kcauto](https://github.com/mrmin123/kcauto/). The tool is written in Python 3 and uses OpenCV for image detection and ADB for input

## Features
* Combat Module &mdash; Automate Combat
* Commission Module &mdash; Automate Commissions
* Mission Module &mdash; Automatic mission management
* Retire Module &mdash; Automatic retirement of common and rare ships

## Requirements
* ADB debugging enabled phone or emulator with 1280x720 resolution

## Installation and Usage
1. Install Python 3.x
2. Clone or download the azurelane-auto repository
3. Install the required packages via `pip3` with the command `pip3 install -r requirements.txt`
4. Run `azurlane-auto` using the command `python3 azurlane-auto.py`

## Updating

The preferred method of keeping azurlane-auto up to date is via git. This requires you have a working [git](https://git-scm.com/) installation, have cloned the azurlane-auto repository, and are running azurlane-auto off of said clone.

If you do have git and cloned the azurlane-auto repository, use one of the following command to update to the latest release (`master` version) of azurlane-auto:

* `git pull origin master` or `git pull`

If you do not have git or a clone of the azurlane-auto repository, head to the [releases page](https://github.com/perryhuynh/azurlane-auto/releases) and download the latest tagged version. Overwrite your local azurlane-auto installation with the contents of the new release, taking care to first back up or not overwrite your config file. **Note that your config file may need updating to be compatible with new releases.**

## License
azurlane-auto is WTFPL licensed, as found in the LICENSE file.

---

## 安装与使用

* 安装`python 3.*`并加入`path`
* 目录下运行`pip3 install -r requirements.txt`
* 安装`ADB`并加入`path`
* 运行`azurlane.py`

## 关于贴图

* 将`map_x-x`如`map_3-4.png`放入`assets`下对应语言中
* 注意:抠图前请先将整个屏幕的截图调为`1920x720`分辨率