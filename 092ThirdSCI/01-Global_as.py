# coding: utf-8
"""
create on May 6, 2020 by Wayne Yu
Function:

获取每个时间，全球活跃的as号


V2：

为地图基础课题第一篇论文输出，重新绘图，使得排版更加的美观
绘制时间修改为19980101-20191201

V3: 20200511

将相关备注修改为英文并将字调大、去掉题头


V4:20200706
编辑想要矢量图svg、pdf、eps，Python均支持，更改下格式即可，也让我Get到了一项矢量图新技能


v5: 20221025
服务于ThirdSCI论文撰写, 19980101-20221001


"""
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import time
import csv


def write_to_csv(res_list, des_path):
    """
    把给定的List，写到指定路径的文件中
    :param res_list:
    :param des_path:
    :return: None
    """
    print("write file <%s> ..." % des_path)
    csv_file = open(des_path, 'w', newline='', encoding='utf-8')
    try:
        writer = csv.writer(csv_file)
        for i in res_list:
            writer.writerow(i)
    except Exception as e:
        print(e)
    finally:
        csv_file.close()
    print("write finish!")


def analysis(open_file):
    """
    对数据进行处理
    :param open_file:
    :return:
    """
    print(open_file)
    # 处理文件名，提取日期信息
    temp_str = open_file.split('\\')[-1]
    date_str = temp_str.split(".")[0][0:4]
    file_read = open(open_file, 'r', encoding='utf-8')
    as_list = []  # 存储当前时间，全部有连接关系的AS
    for line in file_read.readlines():
        if line.strip().find("#") == 0:
            continue
        # print(line.strip())
        """
        每新增一个AS记录，就判断是否在AS列表中，在进行操作，耗时124s
        """
        # if line.strip().split('|')[0] not in as_list:
        #     as_list.append(line.strip().split('|')[0])
        # if line.strip().split('|')[1] not in as_list:
        #     as_list.append(line.strip().split('|')[1])
        as_list.append(line.strip().split('|')[0])
        as_list.append(line.strip().split('|')[1])
    as_list = list(set(as_list))  # 先转换为字典，再转化为列表，速度还可以
    as_list.sort(key=lambda i: int(i))
    # print(as_list)
    # print("Active AS：", len(as_list))
    return date_str, len(as_list)


def draw(x_list_in, y_list_in, save_name_in):
    """
    对传入的数据进行绘图
    :param x_list_in:
    :param y_list_in:
    :param save_name_in:
    :return:
    """
    fig, ax = plt.subplots(1, 1, figsize=(19.2, 10.8))
    plt.xticks(rotation=32)
    plt.tick_params(labelsize=32)
    # plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    font = {'family': 'Times New Roman',
            'style': 'normal',
            'weight': 'normal',
            'color': 'black',
            'size': 42
            }
    # font_legend = {'family': 'sans-serif',
    #                'style': 'normal',
    #                'weight': 'normal',
    #                'size': 28
    #                }
    tick_spacing = 4
    # title_string = "全球互联网网络数量增长趋势（19980101-20191201） "
    # ax.set_title(title_string, font)
    ax.plot(x_list_in, y_list_in, ls='-')
    ax.set_xlabel('Time of estimation', font)
    ax.set_ylabel('Number of networks', font)
    # ax.legend(prop=font_legend)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    ax.grid(True)
    fig.tight_layout()
    save_fig_name = "../000LocalData/Paper_Data_Third/01_" + save_name_in + "_en.png"
    plt.savefig(save_fig_name, dpi=600)
    # plt.show()


if __name__ == "__main__":
    time_start = time.time()  # 记录启动时间
    active_as = []  # 记录活跃的as号
    file_path = []
    for root, dirs, files in os.walk("..\\000LocalData\\as_relationships\\serial-5"):
        for file_item in files:
            file_path.append(os.path.join(root, file_item))
    # print(file_path)
    temp_list = []
    x_list = []
    y_list = []
    for path_item in file_path:
        # print(analysis(path_item))
        x_date, y_cnt = analysis(path_item)
        temp_list.append(x_date)
        x_list.append(x_date)
        temp_list.append(y_cnt)
        y_list.append(y_cnt)
        active_as.append(temp_list)
        print(temp_list)
        temp_list = []
    # print(active_as)
    save_path = "../000LocalData/Paper_Data_Third/01_active_as.csv"
    write_to_csv(active_as, save_path)
    draw(x_list, y_list, "active_as")
    time_end = time.time()
    print("=>Scripts Finish, Time Consuming:", (time_end - time_start), "S")
