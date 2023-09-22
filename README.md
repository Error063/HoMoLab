<p align="center">
  <img src="https://img1.imgtp.com/2023/08/11/UAt1X7KD.png" height="200">
  <br>
  <a href="https://github.com/Error063/HoMoLab" style="text-decoration: none;">
    <img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/Error063/HoMoLab?style=flat-square">
  </a>
  <br>
  <a href="https://github.com/Error063/HoMoLab/issues" style="text-decoration: none;">
    <img alt="GitHub issues" src="https://img.shields.io/github/issues/Error063/HoMoLab?style=flat-square">
  </a>
  <a href="https://github.com/Error063/HoMoLab/discussions" style="text-decoration: none;">
    <img alt="GitHub discussions" src="https://img.shields.io/github/discussions/Error063/HoMoLab?color=%23555&style=flat-square">
  </a>
  <a href="https://github.com/Error063/HoMoLab/graphs/contributors" style="text-decoration: none;">
    <img alt="GitHub contributors" src="https://img.shields.io/github/contributors/Error063/HoMoLab?color=%23c0c0c0&style=flat-square">
  </a>
  <br>
  <a href="https://github.com/Error063/HoMoLab/blob/master/LICENSE" style="text-decoration: none;">
    <img alt="Github license" src="https://img.shields.io/static/v1?style=flat-square&label=license&message=GPL3&color=blueviolet">
  </a>
  <a href="https://github.com/Error063/HoMoLab/commits/main" style="text-decoration: none;">
    <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/Error063/HoMoLab?color=%23114514&style=flat-square">
  </a>
  <a href="https://github.com/Error063/HoMoLab/stargazers" style="text-decoration: none;">
    <img alt="GitHub repo stars" src="https://img.shields.io/github/stars/Error063/HoMoLab?color=%23aa4499&style=flat-square">
  </a>
  <a href="https://github.com/Error063/HoMoLab/forks" style="text-decoration: none;">
    <img alt="GitHub forks" src="https://img.shields.io/github/forks/Error063/HoMoLab?color=%23456789&style=flat-square">
  </a>
</p>

<h1 align="center">HoMoLab</h1>
<p align="center">基于Pywebview的米游社PC客户端实现</p>

---

## 已弃用

由于本项目已重构并拆分为[libmiyoushe (米游社依赖库)](https://github.com/Error063/libmiyoushe)和[ReHomoLab(重构版，未开放)](https://github.com/Error063/ReHomoLab)两部分，因此本项目不再维护

---

## 安装及使用

1. 安装[Python](https://www.python.org/downloads)和pip
2. 命令行运行 `pip install HoMoLab` (Linux则为`pip3 install HoMoLab`)

启动：命令行运行 `python -m homo.lab` (Linux则为`python3 -m homo.lab`)

---

## 声明

1. 根据上游项目的协议要求，本项目遵守GPL3协议。

2. 由于本项目的特殊性，可能随时停止开源或删档。

3. 为了实现用户登录功能，本程序会在用户目录下存储用户登录凭据，您应当妥善保存该凭据。任何因为您的不当操作而导致登录凭据泄露，本程序不负任何责任。

---

## 特点

  1. 轻量：Windows平台使用pyinstaller打包后仅18MB左右（版本0.9.0，使用Edge Webview2）
  2. 跨平台（理论）：借助Pywebview的特性，可以在任意平台（Windows、Linux、macOS）调用内置浏览器使用

---

## 系统要求

任意支持Python 3.10及以上Python版本和GUI的操作系统并且使用pip安装项目根目录下的requirements.txt，兼容的渲染引擎可参考[Web engine | pywebview (flowrl.com)](https://pywebview.flowrl.com/guide/renderer.html)

为保证最佳兼容性，建议在Windows 10及其更新操作系统上运行，并且支持[Edge Webview2](https://developer.microsoft.com/zh-cn/microsoft-edge/webview2/#download-section)运行环境


---

## 已知问题

​	1.由于[pywebview的问题](https://pywebview.flowrl.com/guide/renderer.html#known-issues-and-limitations)，在Linux中，渲染引擎为GTK Webkit2时，部分按钮无法正常工作

---

## 鸣谢

本项目基于（或参考）以下开源项目开发（排名不分先后）


- [UIGF-org/mihoyo-api-collect: 收集米哈游旗下的游戏与应用的API。](https://github.com/UIGF-org/mihoyo-api-collect)。
- [lingduzero666/MihoyoBBS-AutoSign: 米游社自动化脚本，支持『崩坏3福利补给』『原神签到福利』『米游币任务』『各频道升级任务』&现已支持多账号](https://github.com/lingduzero666/MihoyoBBS-AutoSign/tree/main)
- [jQuery](https://jquery.com/)
- [Quill](https://quilljs.com/)
- [pywebview](https://pywebview.flowrl.com/)
- [Flask](https://flask.palletsprojects.com/)

