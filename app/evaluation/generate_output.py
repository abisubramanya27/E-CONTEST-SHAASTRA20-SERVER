import os
import subprocess
import re

count = 1

proc = subprocess.Popen(["g++","./compiler/compiler.cpp"])
proc.wait()

for filename in os.listdir('./input/qn5') :
	if 'tc' in filename :
		fno = re.sub('[^0-9]+','',filename)
		outputfilePath = './expected_output/qn5/output-' + str(fno) + '.txt'
		with open(outputfilePath,'w+') as file :
			count += 1
			inpfilePath = './input/qn5/' + filename
			try :
				proc = subprocess.Popen(["./a.out", './compiler/program.txt', inpfilePath, outputfilePath])
				proc.wait()
			except subprocess.CalledProcessError :
				print(proc)


os.remove('a.out')
	