import json
import sys

print(sys.argv)

json_file = "cdk.json"
with open(json_file) as f_in:
    json_decoded = json.load(f_in)

json_decoded["context"]["branch_name"] = sys.argv[1]

with open(json_file, "w") as f_out:
    json.dump(json_decoded, f_out)
