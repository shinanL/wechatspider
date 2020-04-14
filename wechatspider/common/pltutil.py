import matplotlib.pyplot as plt

from matplotlib.font_manager import FontProperties
font_set = FontProperties(fname='/Library/Fonts/Songti.ttc', size=15)



def plot_single_figure(x, y, title, xlabel, ylabel, name):
    # 设置画布大小
    plt.figure()

    # 标题
    plt.title(title, fontproperties=font_set)

    # 横坐标描述
    plt.xlabel(xlabel, fontproperties=font_set)

    # 纵坐标描述
    plt.ylabel(ylabel, fontproperties=font_set)

    # 数据
    plt.plot(x, y, marker='o')
    # plt.plot(x, y)

    # 设置数字标签
    for a, b in zip(x, y):
        plt.text(a, b, b, ha='center', va='bottom', fontsize=12)

    plt.legend()
    plt.savefig(name)
    plt.close()
