import boto.ec2
from fabric.api import env, run, parallel, sudo, put, cd, settings
from fabric.contrib.project import rsync_project

def set_hosts():
  conn = boto.ec2.connect_to_region(env.awsregion);
  i = []

  for reservation in conn.get_all_instances(filters = { 'tag:Purpose': 'Microservice', 'tag:Microservice': env.microservice, 'tag:MicroserviceApiVersion': env.microserviceapiversion, 'instance-state-name': 'running'}): 
    print reservation.instances
    for host in reservation.instances: 
     i.append('ec2-user@' + str(host.public_dns_name))
  return i

env.hosts = set_hosts()

@parallel
def deploy():
  with cd('/microservice'):
    run('mkdir -p ' + env.sha);
    rsync_project(local_dir='.', remote_dir='/microservice/' + env.sha, exclude=['node_modules', '.git', 'test', 'fabric', 'coverage', '.gitignore', '.jshintrc', 'circle.yml']);
  with cd('/microservice/' + env.sha):
    run('npm install --production')

@parallel
def switch():
  run('ln -sfn /microservice/' + env.sha + ' /microservice/current')
  run('naught deploy')
  with cd('/microservice/' + env.sha):
    with settings(warn_only=True):
      run('ls -t | tail -n +8 | xargs sudo rm -r')
