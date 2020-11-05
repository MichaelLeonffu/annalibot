# annali_marathon.py

# Runs annali bot on loop even after she closes

# Subprocess
import subprocess

bash = "python3 -B annapythonli.py"

print("Starting marathon")
while True:
	process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
	output, error = process.communicate()

	print("output: " + str(output))
	print("error: " + str(error))

print("Marathon done")