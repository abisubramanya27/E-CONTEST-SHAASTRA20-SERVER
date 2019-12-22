import filecmp
import os
import subprocess
import re

noTC = {'1': 1,'2': 19,'3': 19,'4': 19,'5': 1}

def score(code,qn_no,pno) :
	"""if 'a.out' not in os.listdir(os.getcwd()) :
		prc = subprocess.Popen(["g++","./evaluation/compiler/compiler.cpp"])
		prc.wait()"""
	count = 0
	inputPath = './evaluation/input/qn'+qn_no
	programPath = './program' + pno + '.txt'
	with open(programPath,'w+') as pfile :
		pfile.write(code)
	for filename in os.listdir(inputPath) :
		if 'tc' in filename :
			fno = re.sub('[^0-9]+','',filename)
			outputfilePath = './output' + pno + '.txt'
			with open(outputfilePath,'w+') as mfile :
				count += 1
				inpfilePath = './evaluation/input/qn' + qn_no + '/' + filename
				proc = subprocess.Popen(["./a.out", programPath , inpfilePath, outputfilePath],stderr = subprocess.PIPE,stdout = subprocess.PIPE)
				try :
					(stdoutdata,stderrdata) = proc.communicate(timeout = 6)
				except subprocess.TimeoutExpired :
					proc.kill()
					(stdoutdata,stderrdata) = proc.communicate()
					mfile.close()
					os.remove(outputfilePath)
					os.remove(programPath)
					return 'TIME LIMIT EXCEEDED'
				if (len(stderrdata) > 0) :
					mfile.close()
					os.remove(outputfilePath)
					os.remove(programPath)
					return 'COMPILATION ERROR'
				elif (len(stdoutdata) > 0) :
					mfile.close()
					os.remove(outputfilePath)
					os.remove(programPath)
					return 'RUNTIME ERROR'						

				with open('./app/evaluation/expected_output/qn'+qn_no+'/output-'+str(fno)+'.txt') as tgtfile :
					if filecmp.cmp(outputfilePath,'./evaluation/expected_output/qn'+qn_no+'/output-'+str(fno)+'.txt') :
						pass
					else :
						mfile.close()
						os.remove(outputfilePath)
						os.remove(programPath)
						return 'WRONG ANSWER'

			
			os.remove(outputfilePath)

	os.remove(programPath)
	return 'CORRECT ANSWER'
