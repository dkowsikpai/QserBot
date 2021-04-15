import sys

from ignite import IgniteData

IDK = sys.argv[1]

Ignite = IgniteData()
print(Ignite.getData(IDK))
# Ignite.removeData(IDK)