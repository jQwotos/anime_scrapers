import os
fileLocation = os.path.realpath(__file__)
directory = os.path.dirname(fileLocation)
print(os.path.join(directory, ".."))
