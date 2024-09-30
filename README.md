# Clash 代理 IP 检查工具

这是一个用于检查 Clash 代理 IP 信息的 Python 工具。它可以获取代理的 IPv4 和 IPv6 地址，以及相关的地理位置、风险评估等信息。

## 功能

- 获取 Clash 代理列表
- 检查每个代理的 IPv4 和 IPv6 地址
- 获取 IP 地址的详细信息（国家、地区、城市等）
- 评估 IP 地址的风险级别
- 获取 Ping0 风险评估
- 将结果保存为 CSV 文件

## 安装

1. 克隆此仓库：

    ```bash
    git clone https://github.com/snailyp/ip-checker.git
    cd ip-checker
    ```

2. 安装依赖：

    ```sh
    pip install -r requirements.txt
    ```

## 配置

编辑 `config.json` 文件以设置您的 Clash 配置：

```json
{
  "external_controller": "http://127.0.0.1:9090",
  "secret": "",
  "select_proxy_group": "GLOBAL",
  "port_start": 42000,
  "max_threads": 20
}
```

- `external_controller`：Clash 外部控制器地址
- `secret`：Clash API 密钥（如果有）
- `select_proxy_group`：要使用的代理组名称
- `port_start`：监听器起始端口
- `max_threads`：最大线程数

## 使用方法

- 运行 clash_config.py，获得 new_clash.yml

    ```bash
    python .\clash_config.py
    ```

- 将 new_clash.yml 以本地文件的方式导入到 clash 客户端工具中，并选中配置

- 运行主程序：

    ```bash
    python main.py
    ```

程序将检查所有可用的代理，并将结果保存在 `ip_infos.csv` 文件中。

## 文件说明

- `main.py`：主程序
- `clash_api.py`：与 Clash API 交互的模块
- `clash_config.py`：处理 Clash 配置的模块
- `ip_checker.py`：检查 IP 信息的模块
- `config.py`：读取配置文件的模块
- `config.json`：配置文件
- `clash.yml`：Clash 配置文件（需要您自己提供）

## 注意事项

- 确保您的 Clash 正在运行，并且外部控制器可访问。
- 该工具可能需要访问外部 API 来获取 IP 信息，请确保您的网络环境允许这些请求。
- 使用多线程可能会对某些 API 服务造成压力，请谨慎设置 `max_threads` 值。

## 贡献

欢迎提交问题报告和拉取请求。

## 许可证

[MIT License](LICENSE)
