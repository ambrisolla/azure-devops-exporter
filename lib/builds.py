import pytz
import requests
import json

from prometheus_client      import Metric
from multiprocessing        import Pool
from datetime               import datetime, timedelta

class Builds:

  def __init__(self, configurations):
    self.config = configurations
    self.api_version = '7.1-preview.7'
    self.currentProjectId = None

  def collect(self):
    pool = Pool(16)
    data = pool.map(self.getFinished, self.config.projects)
    
    for project in data:
      if project['count'] > 0:
        for build in project['value']:
          
          reason = build['reason']
          
          labels = {
            'id' : str(build['id']),
            'buildNumber'  : str(build['buildNumber']),
            'status'       : build['status'],
            'result'       : build['result'],
            'queueTime'    : build['queueTime'],
            'startTime'    : build['startTime'],
            'finishTime'   : build['finishTime'],
            'projectId'    : build['project']['id'],
            'projectName'  : build['project']['name'],
            'name'         : build['definition']['name'],
            'sourceBranch' : build['sourceBranch'].replace('refs/heads/',''),
            'reason'       : reason,
          }
          
          if reason == 'pullRequest':
            labels['triggeredBy'] = build['triggerInfo']['pr.sender.name']
          elif reason == 'manual':
            labels['triggeredBy'] = build['requestedFor']['uniqueName']
          else:
            labels['triggeredBy'] = ""

          azure_devops_build_status = Metric(
            'azure_devops_build_status',
            'azure_devops_build_status', 
            'gauge')
          azure_devops_build_status.add_sample(
            'azure_devops_build_status', 
            value=1, 
            labels=labels)
          yield azure_devops_build_status
          
          startTime = datetime.strptime(
            build['startTime'].split('.')[0], 
            '%Y-%m-%dT%H:%M:%S')
          finishtime = datetime.strptime(
            build['finishTime'].split('.')[0], 
            '%Y-%m-%dT%H:%M:%S')
          build_latency = ( finishtime - startTime ).total_seconds()
          
          azure_devops_build_latency = Metric(
            'azure_devops_build_latency', 
            'azure_devops_build_latency', 
            'gauge')
          azure_devops_build_latency.add_sample(
            'azure_devops_build_latency', 
            value=int(build_latency), 
            labels=labels)
          yield azure_devops_build_latency
          

  
  def getFinished(self, projectId):

    mt = (datetime.now(pytz.UTC) - timedelta(seconds=self.config.scrape_seconds))

    minTime = f'{mt.year}-{mt.month}-{mt.day}T{str(mt.hour).zfill(2)}:{str(mt.minute).zfill(2)}'
  
    request = requests.get(
            f'{self.config.url}/{self.config.organization}/{projectId}/_apis/build/builds?api-version={self.api_version}&minTime={minTime}&queryOrder=finishTimeDescending',
            auth=self.config.auth)
    
    if request.status_code != 200:
      print(f'Error ({request.status_code}): {request.reason}')
    else:
      return json.loads(request.text)