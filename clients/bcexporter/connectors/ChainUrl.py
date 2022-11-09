from config.Config import Config
import ipaddress
import re

class ChainUrl():

    def __init__(self, endpoint):
        self.endpoint = endpoint

    def get_endpoint(self):
        return self.endpoint

    def get_alias(self):
        return Config().alias
    
    def __str__(self):
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