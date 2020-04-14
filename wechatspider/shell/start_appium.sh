#!/bin/bash
# 批量开启appium服务，脚本执行时传入参数$1，表示开启的服务个数

a=4723
b=9515
logpath='/Users/liushinan/wechat/logs/'
for ((i=0; i<$1*2; i++))
do
	nohup appium -p $[a+i] -bp $[a+i+1] --chromedriver-port $[b+i] --log ${logpath}appium_server${i}.log --local-timezone >/dev/null 2>&1 &
	let i+=1
done


