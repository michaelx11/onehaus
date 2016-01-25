import credentials
import digitalocean
import json
import sys

class DropletDestroyerByName:

    def __init__(self, inputDict):
        self.inputDict = inputDict
        self.verify()

    def verify(self):
        if "name" not in self.inputDict:
            self.exitWithError("Missing droplet name")

    def execute(self):
        manager = digitalocean.Manager(token=credentials.API_TOKEN)
        droplets = manager.get_all_droplets()
        for droplet in droplets:
            if droplet.name == self.inputDict['name']:
                droplet.destroy()
                self.exitCleanly()

        self.exitWithError("Couldn't find droplet with name: %s" % self.inputDict['name'])

    def exitWithError(self, errorMsg):
        errorDict = { "error" : errorMsg }
        print(json.dumps(errorDict))
        sys.exit(1)

    def exitCleanly(self):
        print(json.dumps({ "success" : "true"}))
        sys.exit(0)

if __name__ == "__main__":
    inp = sys.stdin.read()
    inputDict = json.loads(inp)
    destroyer = DropletDestroyerByName(inputDict)
    destroyer.execute()
    destroyer.exitCleanly()
