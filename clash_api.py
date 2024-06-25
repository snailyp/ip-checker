from urllib.parse import quote
import requests
from config import config

headers = {}
if config['secret']:
    headers['Authorization'] = f'Bearer {config["secret"]}'


def fetch_proxies():
    response = requests.get(f'{config["external_controller"]}/proxies', headers=headers)
    # 获取原始数组
    proxies = response.json().get('proxies')
    # 定义需要过滤掉的元素类型列表
    filtered_types = ["LoadBalance", "Selector", "URLTest", "Fallback", "Compatible", "Direct", "Reject", "RejectDrop",
                      "Pass"]
    # 过滤后的代理数组
    filtered_proxies = []
    for key in proxies.keys():
        if proxies[key]['type'] in filtered_types:
            continue
        else:
            filtered_proxies.append(key)

    # 对配置的节点组进行延迟测试, 返回有延迟的代理，去除延迟测试失败的代理
    checked_proxies = delay_test()
    if checked_proxies:
        filtered_proxies = [proxy for proxy in filtered_proxies if proxy in checked_proxies]
    print(f"filtered_proxies:\n{filtered_proxies}")
    return filtered_proxies


def delay_test():
    try:
        response = requests.get(
            f'{config["external_controller"]}/group/{config["select_proxy_group"]}/delay?url=https://www.google.com'
            f'/generate_204&timeout=5000', proxies=config['proxy'])
        print(f"delay_test:\n{response.json()}")
        return response.json()
    except:
        return None


def select_proxy(proxy):
    # 对 proxy 进行编码
    encoded_proxy = quote(f'{config["select_proxy_group"]}')
    # print(f'{config["external_controller"]}/proxies/{encoded_proxy}')
    data = {
        "name": proxy
    }
    try:
        requests.put(url=f'{config["external_controller"]}/proxies/{encoded_proxy}', json=data, headers=headers)
        print(f'{proxy} selected')
        return True
    except:
        return False


if __name__ == '__main__':
    filtered_proxies = fetch_proxies()
    print(filtered_proxies)
    choose_result = select_proxy(filtered_proxies[0])
    delay_test()
