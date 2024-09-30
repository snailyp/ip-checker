import logging
from urllib.parse import quote
import requests
from config import config

# 设置日志配置
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

headers = {}
if config["secret"]:
    headers["Authorization"] = f'Bearer {config["secret"]}'


def fetch_proxies():
    try:
        response = requests.get(
            f'{config["external_controller"]}/proxies', headers=headers
        )
        response.raise_for_status()
        proxies = response.json().get("proxies", {})
        logger.info(f"Retrieved {len(proxies)} proxies")

        filtered_types = [
            "LoadBalance",
            "Selector",
            "URLTest",
            "Fallback",
            "Compatible",
            "Direct",
            "Reject",
            "RejectDrop",
            "Pass",
        ]
        filtered_proxies = [
            key for key, value in proxies.items() if value["type"] not in filtered_types
        ]
        logger.info(f"Remaining {len(filtered_proxies)} proxies after filtering")

        checked_proxies = delay_test()
        if checked_proxies:
            filtered_proxies = [
                proxy for proxy in filtered_proxies if proxy in checked_proxies
            ]
            logger.info(f"Remaining {len(filtered_proxies)} proxies after delay test")

        logger.debug(f"Filtered proxy list: {filtered_proxies}")
        return filtered_proxies
    except requests.RequestException as e:
        logger.error(f"Error occurred while fetching proxy list: {e}")
        return []


def delay_test():
    try:
        url = f'{config["external_controller"]}/group/{config["select_proxy_group"]}/delay'
        params = {"url": "https://www.google.com/generate_204", "timeout": 5000}
        response = requests.get(url, params=params)
        response.raise_for_status()
        result = response.json()
        logger.info(f"Delay test completed, tested {len(result)} proxies")
        logger.debug(f"Delay test results: {result}")
        return result
    except requests.RequestException as e:
        logger.error(f"Error occurred during delay test: {e}")
        return None


def select_proxy(proxy):
    try:
        encoded_proxy = quote(f'{config["select_proxy_group"]}')
        url = f'{config["external_controller"]}/proxies/{encoded_proxy}'
        data = {"name": proxy}
        response = requests.put(url=url, json=data, headers=headers)
        response.raise_for_status()
        logger.info(f"Successfully selected proxy: {proxy}")
        return True
    except requests.RequestException as e:
        logger.error(f"Error occurred while selecting proxy {proxy}: {e}")
        return False


if __name__ == "__main__":
    logger.info("Starting main program")
    filtered_proxies = fetch_proxies()
    if filtered_proxies:
        choose_result = select_proxy(filtered_proxies[0])
        if choose_result:
            delay_test()
    logger.info("Main program execution completed")
