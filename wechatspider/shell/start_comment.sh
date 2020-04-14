#!/bin/bash

# 文章内容和用户评论守护进程
# 需要有入参，如3表示3个设备

function contains() {
    local n=$#
    local value=${!n}
    for ((i=1;i < $#;i++)) {
        if [ "${!i}" == "${value}" ]; then
            echo "y"
            return 0
        fi
    }
    echo "n"
    return 1
}


logpath='/Users/liushinan/wechat/logs/'
pythonpath='/anaconda3/envs/python35/bin/python'
scriptpath='/Users/liushinan/PycharmProjects/wechatspider/comment/article_comment.py'

echo `date "+%Y-%m-%d %H:%M:%S"` 'restart' >> /Users/liushinan/wechat/logs/log.log &&  # 日志中记录脚本开始时间
 
# ps -ef | grep article_comment | awk '{print $2}' | xargs kill -9 ||  # 杀死进程，此处可以省略||，（用|| 而没用&& ，因为此命令运行后会出现kill: xxxx: No such process 错误，|| 的意思是出现错误后执行接下来的语句，而&&是没有错误的情况下执行接下来的语句）

data=(`ps -ef|grep article_comment| grep -v grep | awk {'print $10'}`) # 单反引号输出结果为多行
echo ${data}
echo "数组长度:"${#data[@]}
while [[ ${#data[@]} -ne $1 ]]; do
    for ((i=0; i<$1; i++))
    do
        if [ $(contains "${data[@]}" "$i") == "y" ]; then
            echo '进程'${i}'已启动';
        else
            nohup $pythonpath $scriptpath $i > /Users/liushinan/wechat/logs/comment${i}.log & # 启动进程
            echo '启动'${i};
        fi
    done
    # sleep 5
    data=(`ps -ef|grep article_comment| grep -v grep | awk {'print $10'}`) # 单反引号输出结果为多行
    echo ${data}
    echo "数组长度:"${#data[@]}
done