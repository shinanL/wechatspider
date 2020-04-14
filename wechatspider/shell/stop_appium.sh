#!/bin/bash

# 没有kill -9 不会杀死正在运行的进程
ps -ef|grep /usr/local/bin/appium |grep -v grep| awk '{print $2}'| xargs kill