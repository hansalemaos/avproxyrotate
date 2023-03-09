# Rotates Avast proxy servers

## pip install avproxyrotate

### Disable ipv6:

#### https://networking.grok.lsu.edu/Article.aspx?articleid=17573

```python
from avproxyrotate import start_avast
start_avast(
    sleeptime_reconnect=3,
    hotkey_change="ctrl+alt+m",  # Changes the proxy server via hotkey
    hotkey_stop="ctrl+alt+n",  # Kills the script
    dns="100.122.0.0",
    rotate_server_each_n_seconds=15,  # changes IP each n seconds
    clear_used_ips_after_n_seconds=3600,  # clears already used IPs during proxy rotation
    path_app=r"C:\Program Files\Avast Software\SecureLine VPN",  # install folder
    path_data=r"C:\ProgramData\Avast Software\SecureLine VPN",  # App data - IPs and tlsdomain are extracted from log files, that means, before you use this function, you have to connect to some avast servers using their app
)
```