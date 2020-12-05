# 神威-太湖之光.
from hpc import Hpc

with Hpc(name="sunway") as sunway:
    print(sunway.run_shell("ls"))