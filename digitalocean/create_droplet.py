import credentials
import digitalocean
import json
import sys

class DropletCreationHelper:

    necessary_args = ["name", "region", "image", "size_slug", "backups"]

    def __init__(self, inputDict):
        self.inputDict = inputDict
        self.verify()

    def verify(self):
        for arg in self.necessary_args:
            if arg not in self.inputDict:
                self.exitWithError("Missing argument: " + arg)

    def execute(self):
        droplet = digitalocean.Droplet(token=credentials.API_TOKEN,
                                       name=self.inputDict['name'],
                                       region=self.inputDict['region'],
                                       image=self.inputDict['image'],
                                       size_slug=self.inputDict['size_slug'],
                                       backups=self.inputDict['backups'])
        droplet.create()

    def exitWithError(self, errorMsg):
        errorDict = { "error" : errorMsg }
        print(json.dumps(errorDict))
        sys.exit(1)

if __name__ == "__main__":
    inp = sys.stdin.read()
    inputDict = json.loads(inp)
    helper = DropletCreationHelper(inputDict)
    helper.execute()
    print(json.dumps({ "success" : "true"}))
    sys.exit(0)
