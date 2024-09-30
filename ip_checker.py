import logging
from lxml import html
import ipaddress
import re
import requests


# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IPChecker:
    def __init__(self, proxy: dict):
        self.proxy = proxy

    def fetch_ipv4(self):
        response = requests.get('https://api.ipify.org?format=json', proxies=self.proxy, timeout=5)
        return response.json().get('ip')

    def fetch_ipv6(self):
        response = requests.get('https://api64.ipify.org?format=json', proxies=self.proxy, timeout=5)
        return response.json().get('ip')

    def fetch_ip_details(self, ip):
        logger.info(f'Fetching IP details for: {ip}')
        try:
            response = requests.get(f"http://ip-api.com/json/{ip}", proxies=self.proxy, timeout=5)
            response.raise_for_status()  # Raise an error for bad status codes
            ip_details = response.json()
            return ip_details
        except requests.exceptions.RequestException as e:
            logger.error(f'Error fetching IP details: {str(e)}')

    def fetch_ip_risk(self, ip):
        logger.info(f'Fetching IP risk for: {ip}')
        try:
            response = requests.get(f"https://scamalytics.com/ip/{ip}", proxies=self.proxy, timeout=5)
            response.raise_for_status()
            risk_data = parse_ip_risk(response.text)
            return risk_data
        except requests.RequestException as error:
            logger.error(f'Error fetching IP risk: {error}')

    def fetch_ping0_risk(self, ip):
        logger.info(f'Fetching Ping0 risk for: {ip}')
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
        }

        try:
            initial_response = requests.get(
                f'https://ping0.cc/ip/{ip}', headers=headers, proxies=self.proxy, timeout=5)
            initial_response.raise_for_status()
            window_x = parse_window_x(initial_response.text)
            if window_x:
                cookies = {"jskey": window_x}
                final_response = requests.get(
                    f'https://ping0.cc/ip/{ip}', headers=headers, cookies=cookies, proxies=self.proxy, timeout=5)
                final_response.raise_for_status()
                ping0_data = parse_ping0_risk(final_response.text)
                return ping0_data
            else:
                logger.warning('Failed to retrieve window.x value.')
        except requests.RequestException as e:
            logger.error(f'Error fetching Ping0 risk: {e}')


def is_valid_ipv6(ip):
    try:
        ipaddress.IPv6Address(ip)
        return True
    except ipaddress.AddressValueError:
        return False


def parse_ip_risk(html):
    logger.info('Parsing IP risk data...')
    score_match = re.search(r'"score":"(.*?)"', html)
    risk_match = re.search(r'"risk":"(.*?)"', html)

    if risk_match:
        risk_data = {
            'score': score_match.group(1) if score_match else None,
            'risk': risk_match.group(1)
        }
        logger.info(f'Parsed risk data: {risk_data}')
        return risk_data

    logger.warning('Failed to parse risk data.')
    return None


def parse_window_x(html):
    logger.info('Parsing window.x value...')
    match = re.search(r"window\.x\s*=\s*'([^']+)'", html)
    window_x = match.group(1) if match else None
    logger.info(f'Parsed window.x: {window_x}')
    return window_x


def parse_ping0_risk(html_content):
    logger.info('Parsing Ping0 risk data...')


    tree = html.fromstring(html_content)

    xpath = {
        "ping0Risk": '//div[@class="line line-risk"]//div[@class="riskitem riskcurrent"]/span[@class="value"]',
        "ipType": '/html/body/div[2]/div[2]/div[1]/div[2]/div[8]/div[2]/span',
        "nativeIP": '/html/body/div[2]/div[2]/div[1]/div[2]/div[10]/div[2]/span'
    }

    ping0_data = {}
    for key, path in xpath.items():
        elements = tree.xpath(path)
        if elements:
            ping0_data[key] = elements[0].text_content().strip()
        else:
            ping0_data[key] = None

    logger.info(f'Parsed Ping0 data: {ping0_data}')
    return ping0_data


if __name__ == '__main__':
    ip_checker = IPChecker({"http": "http://127.0.0.1:42001",
                            "https": "http://127.0.0.1:42001"})
    ip = ip_checker.fetch_ipv4()
    ip_checker.fetch_ip_details(ip)
    ip_checker.fetch_ip_risk(ip)
    ip_checker.fetch_ping0_risk(ip)
