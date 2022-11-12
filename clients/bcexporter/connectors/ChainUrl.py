import ipaddress
import re
from config.Config import Config


class ChainUrl:

    def __init__(self, endpoint, alias=None):
        self.endpoint = endpoint
        self.alias = Config().alias

    def get_alias(self) -> str:
        return self.alias

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
                endpoint += self.get_alias()
        finally:
            return endpoint
