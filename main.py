import ipchecker
import clashapi
import pandas as pd


def save_to_excel(data, filename):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"Data saved to {filename}")


if __name__ == '__main__':
    # 获取所有代理
    proxies = clashapi.fetch_proxies()
    ip_infos = []

    # 遍历代理
    for proxy in proxies:
        ip_info = {'name': proxy}
        # 选择一个代理
        clashapi.choose_proxy(proxy)
        delay_test = clashapi.delay_test()
        if not delay_test:
            continue
        # 获取ipv4
        try:
            ip_info['ipv4'] = ipchecker.fetch_ipv4()
        except:
            continue
        # 获取ipv6
        try:
            ipv6 = ipchecker.fetch_ipv6()
            if ipchecker.is_valid_ipv6(ipv6):
                ip_info['ipv6'] = ipv6
            else:
                ip_info['ipv6'] = 'None'
        except:
            pass

        ip_details = ipchecker.fetch_ip_details(ip_info['ipv4'])
        if ip_details:
            ip_info['country'] = ip_details['country']
            ip_info["countryCode"] = ip_details['countryCode']
            ip_info['region'] = ip_details['region']
            ip_info['regionName'] = ip_details['regionName']
            ip_info['city'] = ip_details['city']
            ip_info['zip'] = ip_details['zip']
            ip_info['lat'] = ip_details['lat']
            ip_info['lon'] = ip_details['lon']
            ip_info['timezone'] = ip_details['timezone']
            ip_info['isp'] = ip_details['isp']
            ip_info['org'] = ip_details['org']
            ip_info['as'] = ip_details['as']

        ip_risk = ipchecker.fetch_ip_risk(ip_info['ipv4'])
        if ip_risk:
            ip_info.update(ip_risk)
        ping0risk = ipchecker.fetch_ping0_risk(ip_info['ipv4'])
        if ping0risk:
            ip_info.update(ping0risk)
        ip_infos.append(ip_info)

    # 保存到excel中
    save_to_excel(ip_infos, 'ip_infos.xlsx')
