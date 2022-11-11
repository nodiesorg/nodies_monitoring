import ipaddress
import re

from config.Config import Config


def get_alias() -> str:
    return Config().alias


class ChainUrl:

    def __init__(self, endpoint):
        self.endpoint = endpoint

    def get_endpoint(self) -> str:
        return self.endpoint

    def __str__(self) -> str:
        endpoint = self.get_endpoint()
        try:
            ip = ipaddress.ip_address(re.sub(r'[^\d.]', '', endpoint))
        except ValueError:
            # IP is domain
            pass
        else:
            if ip.is_private:
                endpoint += get_alias()
        finally:
            return endpoint
