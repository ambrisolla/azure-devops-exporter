#!/usr/bin/env python3

from prometheus_client import start_http_server, REGISTRY
from argparse import ArgumentParser
import time

from lib.projects import Projects
from lib.pipelines import Pipelines
from lib.builds import Builds

class Configurations:

    def __init__(self):

        arg = ArgumentParser()
    
        arg.add_argument(
            '--pat', 
            help='Azure Devops PAT', 
            required=True)

        arg.add_argument(
            '--org', 
            help='Azure DevOps Organization', 
            required=True)
        
        arg.add_argument(
            '--http-server-port', 
            help='Port to start http-server', 
            required=True)
        
        arg.add_argument(
            '--scrape-seconds', 
            help='Consider events executed  at N seconds ago.', 
            required=True)
        
        arg.add_argument(
            '--projects', 
            help='Project to be scanned', 
            required=True)

        args = vars(arg.parse_args())
        
        self.pat              = args['pat']
        self.auth             = ( "", self.pat )
        self.url              = 'https://dev.azure.com'
        self.http_server_port = int(args['http_server_port'])
        self.organization     = args['org']
        self.projects         = args['projects'].split(',')
        self.scrape_seconds   = int(args['scrape_seconds'])

if __name__ == '__main__':

    # Load configurations
    configurations = Configurations()
    
    # Create registry passing loaded configurations
    REGISTRY.register(Projects(configurations))
    REGISTRY.register(Pipelines(configurations))
    REGISTRY.register(Builds(configurations))
    
    # start http server
    start_http_server(configurations.http_server_port)

    # Keep http server running
    while True:        
        time.sleep(1)
