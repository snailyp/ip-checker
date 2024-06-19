from urllib.parse import quote

import requests

from config import config


def fetch_proxies():
    response = requests.get(f'{config["external_controller"]}/proxies')
    # 获取原始数组
    proxies = response.json().get('proxies').get('延迟选优').get("all")
    # 定义需要过滤掉的元素列表
    filter_elements = ["延迟选优", "故障转移", "负载均衡(散列)", "负载均衡(轮询)"]
    # 过滤数组
    filtered_proxies = [proxy for proxy in proxies if proxy not in filter_elements]
    return filtered_proxies


def delay_test():
    try:
        requests.get(f'https://www.google.com/generate_204', timeout=5, proxies=config['proxy'])
        return True
    except:
        return False


def choose_proxy(proxy):
    # 对 proxy 进行编码
    encoded_proxy = quote("节点选择")
    # print(f'{config["external_controller"]}/proxies/{encoded_proxy}')
    data = {
        "name": proxy
    }
    try:
        requests.put(url=f'{config["external_controller"]}/proxies/{encoded_proxy}', json=data)
        print(f'{proxy} 选中成功')
        return True
    except:
        return False


if __name__ == '__main__':
    filtered_proxies = fetch_proxies()
    print(filtered_proxies)
    choose_result = choose_proxy(filtered_proxies[0])
    # delay_test()
