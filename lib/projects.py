from prometheus_client      import Metric
from multiprocessing        import Pool

import requests
import json

class Projects:

    def __init__(self, configurations):
        self.config      = configurations
        self.api_version = '7.1-preview.4'
        
    def collect(self):
        
        pool = Pool(16)
        data = pool.map(self.get, self.config.projects)
        
        project_state = {
            'all'           : 0,
            'createPending' : 1,
            'deleted'       : 2,
            'deleting'      : 3,
            'new'           : 4,
            'unchanged'     : 5,
            'wellFormed'    : 6
        }

        for labels in data:
            
            azure_devops_project_info = Metric(
                'azure_devops_project_info',
                'Info about Azure Devops Project',
                'gauge')
            azure_devops_project_info.add_sample(
                'azure_devops_project_info',
                value=project_state[labels['state']],
                labels=labels)
        
            yield azure_devops_project_info

    def get(self, projectId):
        
        request = requests.get(
            f'{self.config.url}/{self.config.organization}/_apis/projects/{projectId}?api-version={self.api_version}',
            auth=self.config.auth)

        if request.status_code != 200:
            print(f'Error ({request.status_code}): {request.text}')
        else:
            data = json.loads(request.text)
            return {
                'id'             : str(data['id']),
                'name'           : str(data['name']),
                'description'    : str(data['description']),
                'url'            : str(data['url']),
                'state'          : str(data['state']),
                'revision'       : str(data['revision']),
                'lastUpdateTime' : str(data['lastUpdateTime'])
            }
