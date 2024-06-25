import concurrent.futures

import ip_checker
import clash_api
import csv
import clash_config


def save_to_csv(ip_infos, filename):
    """
    将数据保存到CSV文件
    :param ip_infos: 二维列表，包含要写入CSV的ip数据
    :param filename: 目标CSV文件名
    """
    # 打开文件，如果不存在则创建
    with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        # 写入表头
        writer.writerow(
            ['name', 'ipv4', 'ipv6', 'country', 'countryCode', 'region', 'regionName', 'city', 'zip', 'lat', 'lon',
             'timezone', 'isp', 'org', 'as', 'score', 'risk', 'ping0Risk', 'ipType', 'nativeIP'])
        # 写入数据
        for ip_info in ip_infos:
            # 使用 get() 方法安全获取字段值，如果字段不存在则返回空字符串
            writer.writerow(
                [ip_info.get('name', ''), ip_info.get('ipv4', ''), ip_info.get('ipv6', ''), ip_info.get('country', ''),
                 ip_info.get('countryCode', ''), ip_info.get('region', ''), ip_info.get('regionName', ''),
                 ip_info.get('city', ''), ip_info.get('zip', ''), ip_info.get('lat', ''), ip_info.get('lon', ''),
                 ip_info.get('timezone', ''), ip_info.get('isp', ''), ip_info.get('org', ''), ip_info.get('as', ''),
                 ip_info.get('score', ''), ip_info.get('risk', ''), ip_info.get('ping0Risk', ''),
                 ip_info.get('ipType', ''), ip_info.get('nativeIP', '')])
        print(f"Data saved to {filename}")


def task(ip_infos, listener):
    print(f"Checking {listener['proxy']}")
    http_proxy = {
        'http': f'http://127.0.0.1:{listener["port"]}',
        'https': f'http://127.0.0.1:{listener["port"]}'
    }
    ipchecker = ip_checker.IPChecker(http_proxy)
    ip_info = {'name': listener['proxy']}
    # 获取ipv4
    try:
        ip_info['ipv4'] = ipchecker.fetch_ipv4()
    except:
        return
        # 获取ipv6
    try:
        ipv6 = ipchecker.fetch_ipv6()
        if ip_checker.is_valid_ipv6(ipv6):
            ip_info['ipv6'] = ipv6
        else:
            ip_info['ipv6'] = ''
    except:
        pass

    ip_details = ipchecker.fetch_ip_details(ip_info['ipv4'])
    if ip_details:
        ip_info.update(ip_details)
    ip_risk = ipchecker.fetch_ip_risk(ip_info['ipv4'])
    if ip_risk:
        ip_info.update(ip_risk)
    ping0risk = ipchecker.fetch_ping0_risk(ip_info['ipv4'])
    if ping0risk:
        ip_info.update(ping0risk)
    ip_infos.append(ip_info)


if __name__ == '__main__':
    # 获取所有代理
    proxies = clash_api.fetch_proxies()
    ip_infos = []

    # 获取所有的listeners
    clash_config = clash_config.ClashConfig()
    listeners = clash_config.get_listeners()
    # 过滤掉不能用的listeners
    filtered_listeners = []
    for listener in listeners:
        if listener['proxy'] in proxies:
            filtered_listeners.append(listener)
        else:
            continue

    with concurrent.futures.ThreadPoolExecutor(max_workers=20, thread_name_prefix='clash-thread') as executor:
        futures = [executor.submit(task, ip_infos, listener) for listener in filtered_listeners]
        concurrent.futures.wait(futures)

    # 保存到excel中
    save_to_csv(ip_infos, 'ip_infos.csv')
