import concurrent.futures
import ip_checker
import clash_api
import csv
import clash_config
from config import config
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def save_to_csv(ip_infos, filename):
    # Open the file, create if it doesn't exist
    with open(filename, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(
            [
                "name",
                "ipv4",
                "ipv6",
                "country",
                "countryCode",
                "region",
                "regionName",
                "city",
                "zip",
                "lat",
                "lon",
                "timezone",
                "isp",
                "org",
                "as",
                "score",
                "risk",
                "ping0Risk",
                "ipType",
                "nativeIP",
            ]
        )
        # Write the data
        for ip_info in ip_infos:
            # Safely get field values using the get() method, return an empty string if the field doesn't exist
            writer.writerow(
                [
                    ip_info.get("name", ""),
                    ip_info.get("ipv4", ""),
                    ip_info.get("ipv6", ""),
                    ip_info.get("country", ""),
                    ip_info.get("countryCode", ""),
                    ip_info.get("region", ""),
                    ip_info.get("regionName", ""),
                    ip_info.get("city", ""),
                    ip_info.get("zip", ""),
                    ip_info.get("lat", ""),
                    ip_info.get("lon", ""),
                    ip_info.get("timezone", ""),
                    ip_info.get("isp", ""),
                    ip_info.get("org", ""),
                    ip_info.get("as", ""),
                    ip_info.get("score", ""),
                    ip_info.get("risk", ""),
                    ip_info.get("ping0Risk", ""),
                    ip_info.get("ipType", ""),
                    ip_info.get("nativeIP", ""),
                ]
            )
        logging.info(f"Data saved to {filename}")


def task(ip_infos, listener):
    logging.info(f"Checking {listener['proxy']}")
    http_proxy = {
        "http": f'http://127.0.0.1:{listener["port"]}',
        "https": f'http://127.0.0.1:{listener["port"]}',
    }
    ipchecker = ip_checker.IPChecker(http_proxy)
    ip_info = {"name": listener["proxy"]}
    # 获取ipv4
    try:
        ip_info["ipv4"] = ipchecker.fetch_ipv4()
    except Exception as e:
        logging.error(f"Failed to fetch IPv4: {e}")
        return
    # 获取ipv6
    try:
        ipv6 = ipchecker.fetch_ipv6()
        if ip_checker.is_valid_ipv6(ipv6):
            ip_info["ipv6"] = ipv6
        else:
            ip_info["ipv6"] = ""
    except Exception as e:
        logging.warning(f"Failed to fetch IPv6: {e}")

    ip_details = ipchecker.fetch_ip_details(ip_info["ipv4"])
    if ip_details:
        ip_info.update(ip_details)
    ip_risk = ipchecker.fetch_ip_risk(ip_info["ipv4"])
    if ip_risk:
        ip_info.update(ip_risk)
    ping0risk = ipchecker.fetch_ping0_risk(ip_info["ipv4"])
    if ping0risk:
        ip_info.update(ping0risk)
    logging.info(f"Completed checking {listener['proxy']}")
    ip_infos.append(ip_info)


if __name__ == "__main__":
    logging.info("Starting main program")

    # Get all proxies
    proxies = clash_api.fetch_proxies()
    ip_infos = []

    # Get all listeners
    clash_config = clash_config.ClashConfig()
    listeners = clash_config.get_listeners()
    # Filter out unavailable listeners
    filtered_listeners = [
        listener for listener in listeners if listener["proxy"] in proxies
    ]
    logging.info(f"Number of filtered listeners: {len(filtered_listeners)}")

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=config["max_threads"], thread_name_prefix="clash-thread"
    ) as executor:
        futures = [
            executor.submit(task, ip_infos, listener) for listener in filtered_listeners
        ]
        concurrent.futures.wait(futures)

    # Save to CSV file
    save_to_csv(ip_infos, "ip_infos.csv")
    logging.info("Main program execution completed")
