# coding:utf-8
"""
create on Oct 23,2018 by Wayne Yu
Function:
该程序旨在对工业园区的出国网速进行测试，并按一定的格式输出报告。
以国家（IP地址）为单位，通过ping和tracert命令去统计丢包率、时延以及经过的路由表。
例：中亚-哈萨克斯坦/95.56.234.66
"""
import subprocess
import threading
import time
import re


def run_ping_test(ip_str):
    """
    进行一组ping的测试，每组n次
    :return:str_ret
    """
    # list_p_r = []
    print("本组测试开始(", ip_str, ")：ping %s -n 10 ", ip_str)
    ftp_sub = subprocess.Popen("ping %s -n 10" % ip_str,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    ret = ftp_sub.stdout.read()
    str_ret = ret.decode('gbk')
    # print(str_ret)
    print("本组测试丢包率(", ip_str, ")：", re.findall('\d+%', str_ret)[0])
    print("本组测试平均时延(", ip_str, ")：", re.findall('\d+ms', str_ret)[-1])


def run_tracert_test(ip_str):
    """
    进行一次tracert命令，输出经过的路由
    :param ip_str:
    :return: tracert_list
    """
    ftp_sub = subprocess.Popen("tracert %s" % ip_str,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    ret = ftp_sub.stdout.read()
    str_ret = ret.decode('gbk')
    print(str_ret)
    print(re.findall("\d+\.\d+\.\d+\.\d+", str_ret))  # 提取所有经过的路由IP地址


if __name__ == "__main__":
    # 例：中亚-哈萨克斯坦/95.56.234.66
    ip_str = "95.56.234.66"
    # run_ping_test(ip_str)
    # run_tracert_test(ip_str)

"""
在windows下使用tracert 命令得到的原输出如下：
通过最多 30 个跃点跟踪
到 vps-1149050-3181.cp.idhost.kz [95.56.234.66] 的路由:

  1     *        *        *     请求超时。
  2     2 ms     2 ms     1 ms  10.6.1.181 
  3     9 ms     3 ms     2 ms  10.8.0.154 
  4     1 ms     1 ms     1 ms  10.8.0.139 
  5     2 ms     2 ms     2 ms  10.8.0.133 
  6     5 ms     7 ms     3 ms  219.239.97.1 
  7     9 ms     6 ms    10 ms  172.30.66.109 
  8    13 ms     5 ms     3 ms  10.255.33.237 
  9     2 ms     2 ms     2 ms  124.205.98.205 
 10     3 ms     3 ms     3 ms  124.205.98.209 
 11     3 ms     3 ms     3 ms  202.99.1.233 
 12     *        *        *     请求超时。
 13     *        *        *     请求超时。
 14    12 ms    11 ms     9 ms  202.106.42.97 
 15     *       16 ms    15 ms  61.148.154.97 
 16    45 ms    47 ms    43 ms  61.51.169.69 
 17    49 ms    41 ms    48 ms  202.96.12.93 
 18    50 ms    47 ms    49 ms  219.158.5.158 
 19    47 ms    47 ms    47 ms  219.158.3.182 
 20   127 ms   127 ms   127 ms  188.128.15.213 
 21   197 ms   199 ms   197 ms  188.254.15.133 
 22   259 ms   253 ms   253 ms  81.177.105.78 
 23   252 ms   253 ms   252 ms  95.59.172.36 
 24   258 ms   258 ms   256 ms  95.59.170.135 
 25   253 ms   255 ms   255 ms  95.59.174.81 
 26   256 ms   256 ms   253 ms  95.56.234.3 
 27   261 ms   259 ms   262 ms  95.56.234.249 
 28   294 ms   295 ms   301 ms  vps-1149050-3181.cp.idhost.kz [95.56.234.66] 

跟踪完成。
"""