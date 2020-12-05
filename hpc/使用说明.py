# 神威-太湖之光.
from hpc import Hpc

with Hpc(name="kamui") as kamui:
    print(kamui.run_shell("ls"))