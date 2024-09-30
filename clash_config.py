import yaml
import logging
from config import config

# 设置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ClashConfig:
    def __init__(self, config_path="clash.yml"):
        self.config_path = config_path
        logger.info(f"Initializing ClashConfig, config file path: {config_path}")
        self.config = self.load_config()
        self.new_config = self.generate_listener_config()

    def load_config(self):
        logger.info(f"Loading configuration file: {self.config_path}")
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                conf = yaml.safe_load(f)
            logger.info("Configuration file loaded successfully")
            return conf
        except Exception as e:
            logger.error(f"Error loading configuration file: {str(e)}")
            raise

    def generate_listener_config(self):
        logger.info("Generating listener configuration")
        new_config = {"listeners": [], "proxies": self.config["proxies"]}
        dns_settings = {
            "enable": True,
            "enhanced-mode": "fake-ip",
            "fake-ip-range": "198.18.0.1/16",
            "default-nameserver": ["114.114.114.114", "223.5.5.5", "8.8.8.8"],
            "nameserver": ["https://doh.pub/dns-query"],
        }

        new_config["dns"] = dns_settings
        for i, proxy in enumerate(self.config["proxies"]):
            listener = {
                "name": f"mixed{i}",
                "type": "mixed",
                "port": config["port_start"] + i,
                "proxy": proxy["name"],
            }
            new_config["listeners"].append(listener)
        logger.info(f"Generated {len(new_config['listeners'])} listeners")
        return new_config

    def get_listeners(self):
        logger.info("Getting listener list")
        return self.new_config["listeners"]

    def save_config(self, new_config, new_config_path="new_clash.yml"):
        logger.info(f"Saving new configuration to: {new_config_path}")
        try:
            with open(new_config_path, "w", encoding="utf-8") as f:
                yaml.dump(new_config, f, allow_unicode=True)
            logger.info("Configuration saved successfully")
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            raise


if __name__ == "__main__":
    try:
        clash_config = ClashConfig("clash.yml")
        clash_config.save_config(clash_config.new_config)
    except Exception as e:
        logger.error(f"Error executing program: {str(e)}")
