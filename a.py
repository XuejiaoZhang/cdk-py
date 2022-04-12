import re

a = "adfeature/CAE-5781/f"
print(re.match("^(feature|bug|hotfix)/CAE-[0-9]+/", a))
