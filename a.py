import subprocess
import re
cmd = 'git branch'
#cmd = 'pwd; ls -al .; git status'

process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
branch_name = str(output.split()[1])
print(branch_name)
