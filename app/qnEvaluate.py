import filecmp
import os
import re
import multiprocessing
from compiler import interpret

noTC = {'1': 1,'2': 19,'3': 19,'4': 19,'5': 16}

def score(code,qn_no,pno) :
	count = 0
	inputPath = './evaluation/input/qn'+qn_no
	for filename in os.listdir(inputPath) :
		if 'tc' in filename :
			fno = re.sub('[^0-9]+','',filename)
			outputfilePath = './evaluation/output' + pno + '.txt'
			with open(outputfilePath,'w+') as mfile :
				count += 1
				inpfilePath = inputPath + '/' + filename
				Q = multiprocessing.Queue()
				prc = multiprocessing.Process(target = interpret,args = (code,inpfilePath,outputfilePath,Q))
				prc.daemon = True
				prc.start()

				prc.join(5)

				if prc.is_alive() :
					prc.terminate()
					prc.join(1)
					mfile.close()
					os.remove(outputfilePath)
					return 'TIME LIMIT EXCEEDED'
				else :
					Message = Q.get()
					if Message == 'ANSWER WRITTEN' :
						with open('./evaluation/expected_output/qn'+qn_no+'/output-'+str(fno)+'.txt') as tgtfile :
							if filecmp.cmp(outputfilePath,'./evaluation/expected_output/qn'+qn_no+'/output-'+str(fno)+'.txt') :
								pass
							else :
								tgtfile.close()
								mfile.close()
								os.remove(outputfilePath)
								return 'WRONG ANSWER'
					else :
						mfile.close()
						os.remove(outputfilePath)
						return Message
			
	os.remove(outputfilePath)
	return 'CORRECT ANSWER'
