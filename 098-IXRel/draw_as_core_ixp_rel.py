# coding:utf-8
"""
create on Nov 3, 2021 By Wenyan YU
Email: ieeflsyu@outlook.com

Function:

参考031/CAICT-Display/draw_as_core_v10.py文件，编写draw_as_core绘图程序，规范化大屏更新操作

# 20230410 高亮呈现12万IXP rel的数据

"""

import time
import csv
import numpy as np
import matplotlib.pyplot as plt


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
        writer = csv.writer(csv_file, delimiter="|")
        for i in res_list:
            writer.writerow(i)
    except Exception as e:
        print(e)
    finally:
        csv_file.close()
    print("write finish!")


def compute_polar_args(as_info):
    """
    根据传入的as_info,计算每个as号的参数angle、radius
    angle = longitue of the AS's orgs
    radius = 1 - log((All_rel(AS)+1) / (maxinum_all_rel + 1))
    :param as_info:
    :return new_as_info:
    """
    new_as_info = []
    max_all_rel = 0  # 存储最大的连接数
    for item in as_info:
        # print(item)
        if int(item[1]) > max_all_rel:
            max_all_rel = int(item[1])
    print("Max Edge Cnt:", max_all_rel)
    for item in as_info:
        angle = 0.0
        radius = 0.0
        if float(item[10]) >= 0.0:
            angle = float(item[10])
        else:
            angle = float(item[10]) + 360.0
        radius = 1 - np.log((int(item[1]) + 1) / (max_all_rel + 1))
        item.append(angle)
        item.append(radius)
        new_as_info.append(item)
        # print(item)
    return new_as_info


def draw_polar_map(as_info, open_file, year_str):
    """
    根据传入的as_info进行绘图
    :param as_info:
    :param open_file:
    :param year_str:
    :return None:
    """
    # #########################关键参数生成##################################
    max_radius = 0.0
    min_radius = 10000.0
    min_index = 0
    angle_list = []
    radius_list = []
    coordinate_dic = {}
    temp_list = []
    item_cnt = 0
    for item in as_info:
        # print(item)
        if float(item[12]) > max_radius:
            max_radius = float(item[12])
        if float(item[12]) < min_radius:
            min_radius = float(item[12])
            min_index = item_cnt
        angle = (float(item[11]) / 360.0) * 2 * np.pi
        radius = float(float(item[12]))
        temp_list.append(angle)
        temp_list.append(radius)
        angle_list.append(angle)
        radius_list.append(radius)
        coordinate_dic[item[0]] = temp_list
        temp_list = []
        item_cnt += 1
    # print(coordinate_dic)
    # 准备绘图
    plt.figure(figsize=(9, 5))
    ax = plt.subplot(111, projection='polar')
    ax.set_ylim(0.0, max_radius + 2)  # 设置极坐标半径radius的最大刻度
    # #########################绘画参数生成##################################
    area_list = []
    lw_list = []
    c_color_list = []
    z_order_list = []
    max_index = []
    cn_index = []
    cn_all_as = []  # 存储所有中国AS号
    global_all_as = []  # 所有世界所有AS号
    index_cnt = 0
    """
    找出所有接入IX的点，并标绿
    """
    ix_rel_file = "./match_rel_result.csv"
    ix_as_list = []
    with open(ix_rel_file, 'r', encoding="utf-8") as f:
        for item_as in f.readlines():
            item_as = item_as.strip().split(",")
            ix_as_list.append(item_as[0])
            ix_as_list.append(item_as[1])
    print("ix_as_list length:", len(ix_as_list), "set:", len(set(ix_as_list)))

    for item in radius_list:
        if item < max_radius * 0.2:
            area_list.append(4)
            lw_list.append(0.1)
            # c_color_list.append([float(200/256), float(100/256), float(100/256)])
            c_color_list.append([float(256 / 256), float(256 / 256), float(256 / 256)])
            z_order_list.append(2)
            max_index.append(index_cnt)  # 记录最牛逼的几个点的坐标
            if as_info[index_cnt][8] == "CN":
                cn_index.append(index_cnt)
        elif item < max_radius * 0.4:
            area_list.append(3)
            lw_list.append(0.1)
            # c_color_list.append([float(224.0/256), float(200.0/256), float(41.0/256)])
            c_color_list.append([float(256 / 256), float(256 / 256), float(256 / 256)])
            z_order_list.append(2)
            if as_info[index_cnt][8] == "CN":
                cn_index.append(index_cnt)
        elif item < max_radius * 0.6:
            area_list.append(2)
            lw_list.append(0.1)
            # c_color_list.append([float(100/256), float(100/256), float(200/256)])
            c_color_list.append([float(256 / 256), float(256 / 256), float(256 / 256)])
            z_order_list.append(2)
            if as_info[index_cnt][8] == "CN":
                cn_index.append(index_cnt)
        else:
            area_list.append(1)
            lw_list.append(0.1)
            c_color_list.append([float(256/256), float(256/256), float(256/256)])
            z_order_list.append(1)

        # 如果该点为ix_as，则改变其填充颜色,改变其Marker，并存储
        if as_info[index_cnt][0] in ix_as_list:
            cn_all_as.append(as_info[index_cnt])  # 存储所有ix_as的AS号
            del c_color_list[-1]
            c_color_list.append([float(100.0/256), float(200.0/256), float(100.0/256)])
        # 存储实世界所有AS号
        global_all_as.append(as_info[index_cnt])
        index_cnt += 1
    area = area_list
    print("CN all AS Length:", len(cn_all_as))
    cn_all_as.sort(reverse=True, key=lambda elem: int(elem[1]))
    print("Global All AS Length:", len(global_all_as))
    global_all_as.sort(reverse=True, key=lambda elem: int(elem[1]))
    # ###########################画线################################
    edges_cnt = 0
    file_read = open(open_file, 'r', encoding='utf-8')
    for line in file_read.readlines():
        if line.strip().find("#") == 0:
            continue
        line = line.strip().split("|")
        p1 = coordinate_dic.get(line[0])
        p2 = coordinate_dic.get(line[1])
        if p1 and p2:

            line_width = 0.01
            line_color = [float(145/256), float(102/256), float(210/256)]
            alpha_value = 1
            z_order_value = 1

            # if p1[1] < max_radius * 0.2 and p2[1] < max_radius * 0.2:
            #     line_width = 0.4
            #     line_color = [float(110/256), float(32/256), float(142/256)]
            #     alpha_value = 1
            #     z_order_value = 6
            # elif p1[1] < max_radius * 0.4 and p2[1] < max_radius * 0.4:
            #     line_width = 0.2
            #     line_color = [float(167/256), float(114/256), float(244/256)]
            #     alpha_value = 0.7
            #     z_order_value = 4
            # elif p1[1] < max_radius * 0.6 and p2[1] < max_radius * 0.6:
            #     line_width = 0.1
            #     line_color = [float(145/256), float(102/256), float(210/256)]
            #     alpha_value = 0.5
            #     z_order_value = 2
            # else:
            #     line_width = 0.02
            #     line_color = [float(62/256), float(132/256), float(132/256)]
            #     z_order_value = 1
            # print("computing:", p1, p2)

            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], linewidth=line_width, alpha=alpha_value, color=line_color, zorder=z_order_value, )
            edges_cnt += 1
    print("edges_cnt:", edges_cnt)

    # #####################二次画线###################
    ix_rel_file = "./match_rel_result.csv"
    ix_rel_cnt = 0
    with open(ix_rel_file, 'r', encoding="utf-8") as f:
        for item in f.readlines():
            item = item.strip().split(",")
            p1 = coordinate_dic.get(item[0])
            p2 = coordinate_dic.get(item[1])
            if p1 and p2:
                z_order_value = 1
                line_width = 0.01
                alpha_value = 0.5
                line_color = [float(62/256), float(132/256), float(132/256)]
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], linewidth=line_width, alpha=alpha_value, color=line_color,
                        zorder=z_order_value, )
                ix_rel_cnt += 1
    print("ix_rel_cnt:", ix_rel_cnt)

    # ######################## 打点######################################
    ax.scatter(angle_list, radius_list, c=c_color_list, edgecolors=[0, 0, 0], marker="s", lw=lw_list, s=area, cmap='hsv', alpha=0.9, zorder=7)
    # ########################绘制外围辅助性图标##########################
    # 画个内圆
    circle_theta = np.arange(0, 2*np.pi, 0.01)
    circle_radius = [max_radius + 0.1] * len(circle_theta)
    # print(circle_theta)
    # print(circle_radius)
    ax.plot(circle_theta, circle_radius, color=[1, 1, 1], linewidth=0.2)
    # 画个外圆1
    circle_theta = np.arange(0, 2*np.pi, 0.01)
    circle_radius = [max_radius + 0.3] * len(circle_theta)
    # print(circle_theta)
    # print(circle_radius)
    ax.plot(circle_theta, circle_radius, color=[1, 1, 1], linewidth=0.2)
    # 画外圆2
    circle_theta = np.arange(0, 2*np.pi, 0.01)
    circle_radius = [max_radius + 0.5] * len(circle_theta)
    # print(circle_theta)
    # print(circle_radius)
    ax.plot(circle_theta, circle_radius, color=[1, 1, 1], linewidth=0.2)
    # 画外圆3
    circle_theta = np.arange(0, 2*np.pi, 0.01)
    circle_radius = [max_radius + 0.6] * len(circle_theta)
    # print(circle_theta)
    # print(circle_radius)
    ax.plot(circle_theta, circle_radius, color=[1, 1, 1], linewidth=0.2)

    # 填充欧洲（Europe）颜色为#bd87bf，从西经14度至东经49度，即346-49
    circle_theta = np.arange(float(346.0/360)*2*np.pi, float(360/360)*2*np.pi, 0.01)
    circle_radius = [max_radius + 0.2] * len(circle_theta)
    ax.plot(circle_theta, circle_radius, color="#bd87bf", linewidth=3)

    circle_theta = np.arange(float(0.0/360)*2*np.pi, float(49/360)*2*np.pi, 0.01)
    circle_radius = [max_radius + 0.2] * len(circle_theta)
    ax.plot(circle_theta, circle_radius, color="#bd87bf", linewidth=3)

    # 填充亚洲（Asia）颜色为#00a895,从东经49度至西经175，即49-185
    circle_theta = np.arange(float(49.0/360)*2*np.pi, float(185/360)*2*np.pi, 0.01)
    circle_radius = [max_radius + 0.2] * len(circle_theta)
    ax.plot(circle_theta, circle_radius, color="#00a895", linewidth=3)

    # 填充北美洲（North American）颜色为#669ed8，从西经170度至西经20度，即190-340
    circle_theta = np.arange(float(190.0/360) * 2 * np.pi, float(340/360) * 2 * np.pi, 0.01)
    circle_radius = [max_radius + 0.2] * len(circle_theta)
    ax.plot(circle_theta, circle_radius, color="#669ed8", linewidth=3)

    # 填充非洲（Africa）颜色为#b680c3，从西经14度至东经52度，即346-52
    circle_theta = np.arange(float(346.0/360) * 2 * np.pi, float(360/360) * 2 * np.pi, 0.01)
    circle_radius = [max_radius + 0.4] * len(circle_theta)
    ax.plot(circle_theta, circle_radius, color="#f3c828", linewidth=3)

    circle_theta = np.arange(float(0.0/360) * 2 * np.pi, float(52/360) * 2 * np.pi, 0.01)
    circle_radius = [max_radius + 0.4] * len(circle_theta)
    ax.plot(circle_theta, circle_radius, color="#f3c828", linewidth=3)

    # 填充大洋洲(Oceana)，颜色为#fec273，从东经110度至东经180度，即110-180
    circle_theta = np.arange(float(110/360) * 2 * np.pi, float(180/360) * 2 * np.pi, 0.01)
    circle_radius = [max_radius + 0.4] * len(circle_theta)
    ax.plot(circle_theta, circle_radius, color="#fec273", linewidth=3)

    # 填充南美洲（South American），颜色为#f2c41d，从西经80度至西经40度，即280-320
    circle_theta = np.arange(float(280/360) * 2 * np.pi, float(320/360) * 2 * np.pi, 0.01)
    circle_radius = [max_radius + 0.4] * len(circle_theta)
    ax.plot(circle_theta, circle_radius, color="#f2c41d", linewidth=3)

    # 绘制经度刻度
    # circle_radius = np.arange(max_radius+0.5, max_radius+0.9, 0.01)
    # circle_theta = [0.0] * len(circle_radius)
    # ax.plot(circle_theta, circle_radius, color=[0, 0, 0], linewidth=0.8)
    # 每隔10度画一个
    for tap_zone in range(0, 36, 1):
        time_zone_angle = tap_zone * 10
        circle_radius = np.arange(max_radius + 0.55, max_radius + 0.8, 0.01)
        circle_theta = [float(time_zone_angle / 360)*2*np.pi] * len(circle_radius)
        ax.plot(circle_theta, circle_radius, color=[1, 1, 1], linewidth=0.3)
    # 每隔90度画一个
    for tap_zone in range(0, 4, 1):
        time_zone_angle = tap_zone * 90
        circle_radius = np.arange(max_radius + 0.55, max_radius + 0.9, 0.01)
        circle_theta = [float(time_zone_angle / 360)*2*np.pi] * len(circle_radius)
        ax.plot(circle_theta, circle_radius, color=[1, 1, 1], linewidth=1)

        # 添加关键城市和地区的文本信息
        # 一般字体统一用字典控制
        font = {'family': 'sans-serif',
                'style': 'italic',
                'weight': 'normal',
                'color': 'white',
                'size': 4
                }
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        text_theta = 0.0
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "伦敦, 英国", fontdict=font, ha='left', va='center', rotation=0)

        text_theta = float(5.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "巴黎, 法国", fontdict=font, ha='left', va='bottom', rotation=5)

        text_theta = float(9.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "法兰克福, 德国", fontdict=font, ha='left', va='bottom', rotation=9)

        text_theta = float(15.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "柏林, 德国", fontdict=font, ha='left', va='bottom', rotation=15)

        text_theta = float(27.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "赫尔辛基, 芬兰", fontdict=font, ha='left', va='bottom', rotation=27)

        text_theta = float(39.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "莫斯科, 俄罗斯", fontdict=font, ha='left', va='bottom', rotation=39)

        text_theta = float(75.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "孟买, 印度", fontdict=font, ha='left', va='bottom', rotation=75)

        text_theta = float(78.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "德里, 印度", fontdict=font, ha='left', va='bottom', rotation=78)

        text_theta = float(100.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "曼谷, 泰国", fontdict=font, ha='right', va='bottom', rotation=100)

        text_theta = float(102.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "新加坡, 新加坡", fontdict=font, ha='right', va='bottom', rotation=102)

        text_theta = float(116.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "北京, 中国", fontdict=font, ha='right', va='bottom', rotation=116)

        text_theta = float(121.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "台北, 中国", fontdict=font, ha='right', va='bottom', rotation=121)

        text_theta = float(139.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "东京, 日本", fontdict=font, ha='right', va='bottom', rotation=139)

        text_theta = float(151.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "悉尼, 澳大利亚", fontdict=font, ha='right', va='bottom', rotation=151)

        text_theta = float(201 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "火奴鲁鲁, 美国", fontdict=font, ha='right', va='top', rotation=201)

        text_theta = float(238.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "圣何塞, 美国", fontdict=font, ha='right', va='top', rotation=238)

        text_theta = float(242.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "圣迭戈, 美国", fontdict=font, ha='right', va='top', rotation=242)

        text_theta = float(248.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "菲尼克斯, 美国", fontdict=font, ha='right', va='top', rotation=248)

        text_theta = float(255.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "丹佛, 美国", fontdict=font, ha='right', va='top', rotation=255)

        text_theta = float(263.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "休斯顿, 美国", fontdict=font, ha='right', va='top', rotation=263)

        text_theta = float(272.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "芝加哥, 美国", fontdict=font, ha='center', va='top', rotation=272)

        text_theta = float(281.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "多伦多, 加拿大", fontdict=font, ha='left', va='top', rotation=281)

        text_theta = float(284.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "华盛顿, 美国", fontdict=font, ha='left', va='top', rotation=284)

        text_theta = float(286.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "渥太华, 加拿大", fontdict=font, ha='left', va='top', rotation=286)

        text_theta = float(289.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "波士顿, 美国", fontdict=font, ha='left', va='top', rotation=289)

        text_theta = float(302.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "布宜诺斯艾利斯, 阿根廷", fontdict=font, ha='left', va='top', rotation=302)

        text_theta = float(316.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "里约热内卢, 巴西", fontdict=font, ha='left', va='top', rotation=316)

        text_theta = float(351.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "阿尔吉斯, 葡萄牙", fontdict=font, ha='left', va='top', rotation=351)

        text_theta = float(354.0 / 360) * 2 * np.pi
        text_radius = max_radius + 1
        ax.text(text_theta, text_radius, "都柏林, 爱尔兰", fontdict=font, ha='left', va='top', rotation=354)

    print("连通度最高的AS号半径：", radius_list[min_index], "ASN:", as_info[min_index][0], "AS info:", as_info[min_index][5])

    plt.axis('off')
    save_fig_name = "./ix_rel_" + year_str + ".jpg"
    plt.savefig(save_fig_name, dpi=1080, facecolor='#202d62')
    # plt.savefig(save_fig_name, dpi=1080, transparent=True)  # 设置背景色为透明
    plt.close()
    return [item_cnt, edges_cnt]


if __name__ == "__main__":
    time_start = time.time()  # 记录启动时间
    as_core_map_info = []
    temp_list = []
    for year_string in range(2022, 2023, 1):
        file_in = '..\\000LocalData\\as_map\\as_core_map_data_new' + str(year_string) + '1001.csv'
        file_read = open(file_in, 'r', encoding='utf-8')
        file_in_list = []
        new_info = []
        asn_temp = ""
        for line in file_read.readlines():
            line = line.strip().split('|')
            if len(line) < 11:
                continue
            if asn_temp == line[0]:
                continue
            file_in_list.append(line)
            asn_temp = line[0]
        new_info = compute_polar_args(file_in_list)  # 计算极坐标相关参数
        bgp_file = "..\\000LocalData\\as_relationships\\serial-1\\" + str(year_string) + "1001.as-rel.txt"
        temp_list.append(str(year_string))
        temp_list.extend(draw_polar_map(new_info, bgp_file, str(year_string)))
        as_core_map_info.append(temp_list)
        temp_list = []
        print(as_core_map_info)
    save_path = "./as_core_map_statistics_info.csv"
    write_to_csv(as_core_map_info, save_path)
    time_end = time.time()
    print("=>Scripts Finish, Time Consuming:", (time_end - time_start), "S")
