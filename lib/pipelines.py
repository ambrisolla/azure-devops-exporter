from prometheus_client import Metric, Gauge
from prometheus_client.core import GaugeMetricFamily
from multiprocessing        import Pool
import requests
import json


class Pipelines:

	def __init__(self, configurations):
		self.config = configurations
		self.api_version = '7.1-preview.1'
		self.currentProjectId = None

	def collect(self):
		yield GaugeMetricFamily('pipeline', 'pipes', value=1)
		
		pool = Pool(20)
		project_pipeline_ids  = pool.map(self.get_ids, self.config.projects)

		for project in project_pipeline_ids:
			
			self.currentProjectId  = project['projectId']
			ids 	  			   = project['ids']

			pool = Pool(20)
			data = pool.map(self.get_papeline_info, ids)
			
			for labels in data:
				
				azure_devops_pipeline_info = Metric(
                	'azure_devops_pipeline_info',
                	'Info about Azure Devops Project',
                	'gauge')
            	
				azure_devops_pipeline_info.add_sample(
                	'azure_devops_pipeline_info',
                	value=1,
                	labels=labels)
				

				yield azure_devops_pipeline_info


		
		

		
	def get_ids(self, projectId):
		req = requests.get(
			f'{self.config.url}/{self.config.organization}/{projectId}/_apis/pipelines?api-version={self.api_version}',
			auth=self.config.auth)
        
		if req.status_code != 200:
			print(f'Error ({req.status_code}): {req.status_code}')
		else:	
			data = json.loads(req.text)
			ids = []
			if data['count'] > 0:
				for pipeline in data['value']:
					ids.append(pipeline['id'])
			return {
				'projectId' : projectId,
				'ids' 		: ids
			}
	
	
	def get_papeline_info(self, id):
		
		req = requests.get(
			f'{self.config.url}/{self.config.organization}/{self.currentProjectId}/_apis/pipelines/{id}?api-version={self.api_version}',
			auth=self.config.auth)
        
		if req.status_code != 200:
			print(f'Error ({req.status_code}): {req.status_code}')
		else:
			data = json.loads(req.text)
			if 'fullName' in data['configuration']['repository']:
				return {
					'name' 		     : str(data['name']),
					'id'   		     : str(data['id']),
					'projectId'      : str(self.currentProjectId),
					'repositoryName' : str(data['configuration']['repository']['fullName']),
					'repositoryType' : str(data['configuration']['repository']['type']),
				}

	
		