import os
import sys
import subprocess
import logging
import re
from glob import glob

logger = logging.getLogger()
logger.setLevel(logging.INFO)



threshold = 0
def pylint_check(bash_command):
#	bashCommand = "pylint tests --ignore=tests/unit,tests/other_tests_2,tests/__pycache__,tests/other_tests"
	logger.info(f"Bash command: {bash_command}")
	process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
	output, error = process.communicate()
	output = output.decode("utf-8")
	logger.info(f"Output: {output}")
	logger.info(f"Error: {error}")

	#print(type(output), output)
	# match = re.match("Your code has been rated at ([0-9.-]+)/10", "Your code has been rated at 1.21/10 (previous run: 1.21/10, +0.00)")
	match = re.match(".*Your code has been rated at ([0-9.-]+)/10", output, re.DOTALL)

	if match:
		score = float(match.groups()[0])
		if score > threshold:
			logger.info(f"score: {score} > threshold: {threshold}")
			print(f"score: {score} > threshold: {threshold}")
		else:
			logger.info(f"score: {score} <= threshold: {threshold}")
			print(f"score: {score} <= threshold: {threshold}")
			sys.exit(-1)
	else:
		print(f"No Pylint score found")
		logger.info(f"No Pylint score found")
		sys.exit(-1)


git_changes = "file_changes.txt"
dirname_list = []
with open(git_changes) as f:
	for file in f.readlines():
		dirname = os.path.dirname(file)
		if dirname == "":
			dirname = "."
		if dirname not in dirname_list:
			dirname_list.append(dirname)

dirname_list = ["tests", "."]
# dirname_list = ["."]


for path in dirname_list:
	sub_dirs = glob(path + "/*/")
	ignore_statement = ""
	for d in sub_dirs:
		d = d.strip("/")
		ignore_statement = ignore_statement + d + ','
	ignore_statement = ignore_statement.strip(',')
	logger.info(f"Path: {path}, ignore_statement: {ignore_statement})")
	pylint_command = f"pylint --output-format=parseable --load-plugins=pylint.extensions.mccabe,pylint.extensions.docparams --max-complexity=10 --reports=y {path} --ignore={ignore_statement}"
	logger.info(f"pylint_command: {pylint_command}")
	print(pylint_command)
	pylint_check(pylint_command)


# def black_check(bash_command):
# 	#bash_command = "black --check -v a.py get_modified_dirs.py"
# 	logger.info(f"Bash command: {bash_command}")
# 	process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
# 	output, error = process.communicate()
# 	output = output.decode("utf-8")
# 	logger.info(f"Output: {output}")
# 	logger.info(f"Error: {error}")
# 	rc = process.returncode
# 	logger.info(f"Return code of black command: {rc}")
# 	print(f"Return code: {rc}")
# 	if rc == 0:
# 		logger.info(f"From Black result: nothing would change")
# 	elif rc == 1:
# 		logger.info(f"From Black result: some files would be reformatted")
# 	else:
# 		if rc == 123:
# 			logger.info(f"From Black result: an internal error")
# 		else:
# 			logger.info(f"Black command error")
# 		sys.exit(-1)


# git_changes = "file_changes.txt"
# #black_statement = "black --check -v --exclude='\.swp|package-lock.json|__pycache__|\.pytest_cache|\.env|\.venv|\.egg-info|\.idea/|\.cdk.staging|cdk.out|cdk.context.json|\.DS_Store|infrastructure/plugins/plugins.zip|\.vscode|\.coverage|plugins/plugins.zip' "
# dirname_list = []
# with open(git_changes) as f:
# 	for file in f.readlines():
# 		file = file.strip("\n")
# 		dirname = os.path.dirname(file)
# 		if dirname == "":
# 			dirname = "."
# 		if dirname not in dirname_list:
# 			dirname_list.append(dirname)

# dirname_list = ["tests", "."]
# # dirname_list = ["."]

# for path in dirname_list:
# 	sub_dirs = glob(path + "/*/")
# 	exclude_statement = "\.swp|package-lock.json|__pycache__|\.pytest_cache|\.env|\.venv|\.egg-info|\.idea/|\.cdk.staging|cdk.out|cdk.context.json|\.DS_Store|infrastructure/plugins/plugins.zip|\.vscode|\.coverage|plugins/plugins.zip"
# 	for d in sub_dirs:
# 		d = d.replace("./", "")
# 		exclude_statement = exclude_statement + '|' + d
# 	black_statement=f'black --check -v {path} --exclude={exclude_statement}'
# 	logger.info(f"black_statement: {black_statement}")
# 	print(black_statement)
# 	black_check(black_statement)
