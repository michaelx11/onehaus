import credentials
import digitalocean
import json

def process_droplet(droplet):
    stats = {}
    stats['name']= droplet.name
    stats['id'] = droplet.id
    stats['memory'] = droplet.memory
    stats['vcpus'] = droplet.vcpus
    stats['disk'] = droplet.disk
    stats['status'] = droplet.status
    return stats

droplets = {}

manager = digitalocean.Manager(token=credentials.API_TOKEN)
droplet_list = manager.get_all_droplets()
for droplet in droplet_list:
    droplets[droplet.name] = process_droplet(droplet)

print json.dumps(droplets)
