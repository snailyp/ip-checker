from lxml import html
import ipaddress
import re
import requests


def fetch_ipv4():
    response = requests.get('https://api.ipify.org?format=json')
    return response.json().get('ip')


def fetch_ipv6():
    response = requests.get('https://api64.ipify.org?format=json')
    return response.json().get('ip')


def is_valid_ipv6(ip_address):
    """
    判断给定的字符串是否为有效的IPv6地址。

    :param ip_address: 待验证的ipv6地址字符串
    :return: 布尔值,如果地址有效返回True,否则返回False
    """
    try:
        ipaddress.IPv6Address(ip_address)
        return True
    except ipaddress.AddressValueError:
        return False


def fetch_ip_details(ip):
    print('Fetching IP details for:', ip)

    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        response.raise_for_status()  # Raise an error for bad status codes
        # print('IP details fetched:', response.text)
        ip_details = response.json()
        return ip_details
    except requests.exceptions.RequestException as e:
        print('Error fetching IP details:', str(e))


def fetch_ip_risk(ip):
    print('Fetching IP risk for:', ip)
    try:
        response = requests.get(f"https://scamalytics.com/ip/{ip}")
        response.raise_for_status()
        # print('IP risk fetched:', response.text)
        risk_data = parse_ip_risk(response.text)
        return risk_data
    except requests.RequestException as error:
        print('Error fetching IP risk:', error)


def parse_ip_risk(html):
    print('Parsing IP risk data...')
    score_match = re.search(r'"score":"(.*?)"', html)
    risk_match = re.search(r'"risk":"(.*?)"', html)

    if risk_match:
        risk_data = {
            'score': score_match.group(1) if score_match else None,
            'risk': risk_match.group(1)
        }
        # print('Parsed risk data:', risk_data)
        return risk_data

    print('Failed to parse risk data.')
    return None


def fetch_ping0_risk(ip):
    print('Fetching Ping0 risk for:', ip)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
    }

    try:
        initial_response = requests.get(
            f'https://ping0.cc/ip/{ip}', headers=headers)
        initial_response.raise_for_status()
        # print('Initial Ping0 response:', initial_response.text)

        window_x = parse_window_x(initial_response.text)
        if window_x:
            cookies = {"jskey": window_x}
            final_response = requests.get(
                f'https://ping0.cc/ip/{ip}', headers=headers, cookies=cookies)
            final_response.raise_for_status()
            # print('Final Ping0 response:', final_response.text)
            ping0_data = parse_ping0_risk(final_response.text)
            return ping0_data
        else:
            print('Failed to retrieve window.x value.')
    except requests.RequestException as e:
        print('Error fetching Ping0 risk:', e)


def parse_window_x(html):
    print('Parsing window.x value...')
    match = re.search(r"window\.x\s*=\s*'([^']+)'", html)
    window_x = match.group(1) if match else None
    print('Parsed window.x:', window_x)
    return window_x


def parse_ping0_risk(html_content):
    print('Parsing Ping0 risk data...')

    # 解析HTML内容
    tree = html.fromstring(html_content)

    # 定义要提取的数据的XPath
    xpaths = {
        "ping0Risk": '/html/body/div[2]/div[2]/div[1]/div[2]/div[9]/div[2]/span',
        "ipType": '/html/body/div[2]/div[2]/div[1]/div[2]/div[8]/div[2]/span',
        "nativeIP": '/html/body/div[2]/div[2]/div[1]/div[2]/div[11]/div[2]/span'
    }

    # 提取数据并存储在字典中
    ping0_data = {key: tree.xpath(f'string({xpath})').strip()
                  for key, xpath in xpaths.items()}
    print('Parsed Ping0 data:', ping0_data)
    return ping0_data


if __name__ == '__main__':
    ip = fetch_ipv4()
    fetch_ip_details(ip)
    fetch_ip_risk(ip)
    fetch_ping0_risk(ip)
