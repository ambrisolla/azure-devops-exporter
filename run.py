from prometheus_client import start_http_server, Summary, Gauge, REGISTRY
from prometheus_client.core import GaugeMetricFamily
import yaml
import time
import os

from lib.projects import Projects
from lib.pipelines import Pipelines


class Configurations:
    
    def __init__(self):
        
        config = yaml.safe_load( open('config.yaml', 'r').read() )

        self.pat              = config['pat']
        self.url              = config['url']
        self.organization     = config['organization']
        self.http_server_port = config['http_server_port']
        self.auth             = ( "", self.pat )
        self.projects         = config['projects']

if __name__ == '__main__':

    # Load configurations
    configurations = Configurations()

    # Create registry passing loaded configurations
    REGISTRY.register(Projects(configurations))
    REGISTRY.register(Pipelines(configurations))
    

    # start http server
    start_http_server(configurations.http_server_port)

    # Keep http server running
    while True:        
        time.sleep(1)
