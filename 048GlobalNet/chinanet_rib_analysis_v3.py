# coding:utf-8
"""
create on Aug 17, 2020 By Wenyan YU
Email：ieeflsyu@outlook.com

Function:

用公开的BGP数据源，可能存在前缀数据的失真的情况，因此最好的方式就是拿C公司的RIB，直接分析其到全球前缀可达的信息
结合AS Path可分析出较为准确的全球可达比例，及其对U国的依赖性

本程序要是通过分析C公司RIB(prefix, as path)，统计其全球可达前缀（IP规模）中第一跳为U国所占的比例
prefix_U_rate、ip_U_rate


V2:
除了占比以外，还需要进一步分析出，剔除U国的影响后，有哪些AS是可达的，可达的前缀都是什么？
然后再把AS信息映射为国家，并在图中标识
操作后，分为两张图，AS网络的打点图以及全球各国AS可达性色块图

影响操作分为两个层次：
第一个层次，最优路由第一跳为U国的；
第二个层次，最优路由AS Path中只要存在U国的AS，则该前缀不可达。

此外还得分析下，三家企业直连网络的数量以及直联网络中U国的数量

以上均为学术研究探讨

V3:
只统计chinanet 两个层次操作后，全球各个国家受影响的占比



"""

import openpyxl
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
    csvFile = open(des_path, 'w', newline='', encoding='gbk')
    try:
        writer = csv.writer(csvFile, delimiter=",")
        for i in res_list:
            writer.writerow(i)
    except Exception as e:
        print(e)
    finally:
        csvFile.close()
    print("write finish!")


def convert_excel2csv(rib_file):
    """
    将Excel数据转换为csv数据，加快处理速度
    :param rib_file:
    :return:
    """
    print(rib_file)
    rib_csv_list = []
    work_book = openpyxl.load_workbook(rib_file)
    for work_sheet in work_book.worksheets:
        row_cnt = 0
        for row in work_sheet.rows:
            temp_list = []
            for cell in row[0:2]:
                print(cell.value, end="")
                temp_list.append(cell.value)
            rib_csv_list.append(temp_list)
            print()
            row_cnt += 1
    save_path = "../000LocalData/as_simulate/v4-route.csv"
    write_to_csv(rib_csv_list, save_path)


def extract_as_info():
    """
    根据asn_info文件，提取as info 信息
    :return:
    """
    file_in = "../000LocalData/as_Gao/asn_info.txt"
    file_in_read = open(file_in, 'r', encoding='utf-8')
    as2country_dict = {}  # 存储as号和国家对应关系的字典
    for line in file_in_read.readlines():
        line = line.strip().split("\t")
        as2country_dict[line[0]] = line[1].split(",")[-1].strip()
    return as2country_dict


def gain_country_cn():
    """
    根据GeoLite2-Country-Locations-zh-CN.csv 获取国家简写到大洲和国家信息
    :return country_info_dict:
    """
    country_info_file = "../000LocalData/as_geo/GeoLite2-Country-Locations-zh-CN.csv"
    country_info_file_read = open(country_info_file, "r", encoding="utf-8")
    country_info_dict = {}
    for line in country_info_file_read.readlines():
        line = line.strip().split(",")
        # print(line[4], line[5], line[3])
        country_info_dict[line[4]] = [line[5], line[3]]
    # print(country_info_dict)
    return country_info_dict


def chinanet_rib_analysis(rib_file, u_as_group):
    """
    根据传入的rib CSV信息，统计在最优路由第一跳为U国的占比
    :param rib_file:
    :param u_as_group:
    :return:
    """
    as2country = extract_as_info()
    country_info_dict = gain_country_cn()
    # print(as2country)
    rib_file_read = open(rib_file, 'r')
    line_cnt = 0  # 记录行数
    invalid_cnt = 0  # 记录无效记录数
    valid_cnt = 0  # 记录有效记录数
    ip_num_cnt = 0  # 根据前缀统计IP规模，用32减去网络号的长度，大约为2的N次方个地址
    prefix_u_cnt = 0  # 记录最优路由第一跳为U国的前缀数量
    ip_num_u_cnt = 0  # 记录最优路由第一跳为U国的IP地址数量
    prefix_u_cnt_anywhere = 0  # 记录最优路由任意一跳含U国的前缀数量
    ip_num_u_cnt_anywhere = 0  # 记录最优路由任意一跳含U过的IP地址数量
    direct_networks_list = []  # 存储该ISP直联网络的列表
    direct_networks_u_list = []  # 存储该ISP直联属于U国的网络列表
    direct_networks_c_list = []  # 存储该ISP直联属于C国的网络列表

    global_reachable_as_list = []  # 存储总的全球可达网络的AS列表
    reachable_as_list_first = []  # 存储第一层次可达的AS列表
    reachable_as_list_second = []  # 存储第二层次可达的AS列表

    for line in rib_file_read.readlines():
        line = line.strip().split(",")
        line_cnt += 1
        # print(line)
        if line[0].find("/") == -1:
            # print(line)
            invalid_cnt += 1
            continue
        if len(line[1].strip()) == 0:
            invalid_cnt += 1
            continue

        ip_prefix = line[0].split("/")
        net_len = int(ip_prefix[1])
        ip_num_cnt += pow(2, (32-net_len))
        valid_cnt += 1
        # print(line[1].strip().split(" "))
        as_path_as = line[1].strip().split(" ")
        # print(as_path_as)
        first_hop_as = as_path_as[0]
        last_hop_as = as_path_as[-1]
        if first_hop_as in u_as_group:
            # print(first_hop_as)
            prefix_u_cnt += 1
            ip_num_u_cnt += pow(2, (32-net_len))
        if first_hop_as not in u_as_group:
            # 如果某AS网有一个前缀可达，则该AS网可达
            reachable_as_list_first.append(last_hop_as.strip("{").strip("}"))
        # try:
        #     if as2country[first_hop_as] != "US":
        #         # 如果某AS网有一个前缀可达，则该AS网可达
        #         reachable_as_list_first.append(last_hop_as.strip("{").strip("}"))
        # except Exception as e:
        #     # print(e)
        #     pass

        # intersection_hop_set = set(as_path_as).intersection(set(u_as_group))

        # print(as_path_as)

        u_flag = 0  # 是否路径是否含U国AS
        for item in as_path_as:
            try:
                item = item.strip("{").strip("}")
                if as2country[item] == "US":
                    u_flag = 1
                    break
            except Exception as e:
                # print(as_path_as)
                pass

        # print(intersection_hop_set)
        if u_flag == 1:
            # 如果路径含U国AS
            # print(intersection_hop_set)
            prefix_u_cnt_anywhere += 1
            ip_num_u_cnt_anywhere += pow(2, (32-net_len))
        if u_flag == 0:
            # 如果某AS网有一个前缀可达，则该AS网可达
            reachable_as_list_second.append(last_hop_as.strip("{").strip("}"))
        direct_networks_list.append(first_hop_as)  # 存储直联网络AS
        global_reachable_as_list.append(last_hop_as.strip("{").strip("}"))  # 存储该条可达前缀所属的AS网络
        try:
            if as2country[first_hop_as] == "US":
                # print(as2country[first_hop_as])
                direct_networks_u_list.append(first_hop_as)  # 存储直联网络为U国的网络
            elif as2country[first_hop_as] == "CN":
                direct_networks_c_list.append(first_hop_as)  # 存储直联网络为C国的网络
        except Exception as e:
            # print(e)
            pass

    # print(len(direct_networks_list))
    # print(len(direct_networks_u_list))
    direct_networks_list = list(set(direct_networks_list))
    direct_networks_u_list = list(set(direct_networks_u_list))
    direct_networks_c_list = list(set(direct_networks_c_list))

    global_reachable_as_list = list(set(global_reachable_as_list))
    reachable_as_list_first = list(set(reachable_as_list_first))
    reachable_as_list_second = list(set(reachable_as_list_second))

    """
    根据0阶段、1阶段、2阶段的各个AS网络，统计分阶段各个国家可达AS网络，然后计算其可达性
    根据可达性，分级统计
    
    然后再根据各大洲各方向，统计3级及其以上的国家个数
    
    分大洲，非洲、亚洲、欧洲、大洋洲、南美洲、北美洲
    分方向，东盟、一带、一路、G20、OECD
    
    """

    temp_list = list()
    for item in global_reachable_as_list:
        temp_list.append([item])
        try:
            # print(country_info_dict[as2country[item]])
            country_info = country_info_dict[as2country[item]]
            # print(country_info[0])
        except Exception as e:
            print(item)
    save_path = "../000LocalData/as_simulate/可达（电信）_0.txt"
    write_to_csv(temp_list, save_path)
    temp_list.clear()
    for item in reachable_as_list_first:
        temp_list.append([item])
        try:
            if as2country[item] == "US":
                # print(item)
                pass
        except Exception as e:
            pass
    save_path = "../000LocalData/as_simulate/可达（电信）_1.txt"
    write_to_csv(temp_list, save_path)
    temp_list.clear()
    for item in reachable_as_list_second:
        temp_list.append([item])
        try:
            if as2country[item] == "US":
                print(item)
                pass
        except Exception as e:
            pass
    save_path = "../000LocalData/as_simulate/可达（电信）_2.txt"
    write_to_csv(temp_list, save_path)

    print("Excel总的行数:", line_cnt)
    print("无效记录数:", invalid_cnt)
    print("有效记录数:", valid_cnt)
    print("总的IP规模(v4):", ip_num_cnt)
    print("最优路由第一跳为U国的前缀数量:%s, 占比(%.6f)" % (prefix_u_cnt, prefix_u_cnt/valid_cnt))
    print("最优路由第一跳为U国的IP地址数量(V4):%s, 占比(%.6f)" % (ip_num_u_cnt, ip_num_u_cnt/ip_num_cnt))
    print("最优路由任意一跳含U国的前缀数量:%s, 占比(%.6f)" % (prefix_u_cnt_anywhere, prefix_u_cnt_anywhere/valid_cnt))
    print("最优路由任意一跳含U国的IP地址数量(V4):%s, 占比(%.6f)" % (ip_num_u_cnt_anywhere, ip_num_u_cnt_anywhere/ip_num_cnt))

    all_reach = len(global_reachable_as_list)
    reach_first = len(reachable_as_list_first)
    reach_second = len(reachable_as_list_second)
    print("\n该ISP可达的全球AS网络数量:", all_reach)
    print("第一层次操作后，该ISP全球可达的AS网络数量:%s, 占比(%.6f)" % (reach_first, reach_first/all_reach))
    print("第二层次操作后，该ISP全球可达的AS网络数量:%s, 占比(%.6f)" % (reach_second, reach_second/all_reach))
    print("注：某AS网络只要有一个前缀可达，则该AS网络可达")

    print("\n该ISP直联网络的数量:", len(direct_networks_list))
    print("该ISP直联网络中为U国的数量:", len(direct_networks_u_list))
    print("该ISP直联网络中为C国的数量:", len(direct_networks_c_list))


def gain_u_as_group():
    """
    根据All AS CSV文件，获取u as group
    :return re_list:
    """
    re_list = []  # 存储返回的list
    all_as_file = "../000LocalData/as_simulate/电信-所有企业.CSV"
    all_as_file_read = open(all_as_file, 'r')
    for line in all_as_file_read.readlines():
        line = line.strip().split(",")
        as_item = line[-1].strip("AS")
        # print(as_item)
        re_list.append(as_item)
    # print(len(re_list))
    return re_list


if __name__ == "__main__":
    time_start = time.time()  # 记录启动时间
    us_as_group = gain_u_as_group()
    # print(gain_u_as_group())
    my_rib_file = "../000LocalData/as_simulate/v4-route.csv"
    chinanet_rib_analysis(my_rib_file, us_as_group)
    # gain_country_cn()
    time_end = time.time()  # 记录结束时间
    print("\n=>Scripts Finish, Time Consuming:", (time_end - time_start), "S")
