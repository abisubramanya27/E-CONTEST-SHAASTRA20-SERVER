MAX_SIZE = 5e6
MAX_CELLS  = 65536
MAX_VAL = 255
MIN_VAL = 0

lineno = 1
ptr = 0
data = [0] * MAX_CELLS
brackets = []

inp_buff = ''
out_buff = ''
inp_ind = 0

def interpret(program,inputPath,outputPath,Q) :
	global MAX_CELLS, MAX_VAL, MIN_VAL, MAX_SIZE
	global lineno, ptr, data, brackets, inp_buff, out_buff, inp_ind

	strlen = len(program)
	if (strlen > MAX_SIZE) :
		Q.put("MEMORY LIMIT EXCEEDED")
		return

	with open(inputPath,'r') as f :
		inp_buff = f.read()
	inp_buff = inp_buff.strip()
	inplen = len(inp_buff)

	ind = 0
	while (ind < strlen) :
		if (program[ind] == '+') :
			if (data[ptr] >= MAX_VAL) :
				data[ptr] = MIN_VAL
			else :
				data[ptr] += 1
		elif (program[ind] == '-') :
			if (data[ptr] <= MIN_VAL) :
				data[ptr] = MAX_VAL
			else :
				data[ptr] -= 1
		elif (program[ind] == '<') :
			ptr -= 1
			if (ptr < 0) :
				ptr = MAX_CELLS-1
		elif (program[ind] == '>') :
			ptr += 1
			if (ptr >= MAX_CELLS) :
				ptr = 0
		elif (program[ind] == ',') :
			if (inp_ind >= inplen) :
				Q.put(f"RUNTIME ERROR : Line {lineno}")
				return
			data[ptr] = ord(inp_buff[inp_ind])
			inp_ind += 1
		elif (program[ind] == '.') :
			out_buff += str(chr(data[ptr]))
		elif (program[ind] == '[') :
			if (data[ptr] != 0) :
				brackets.append([ind,lineno])
			else :
				ob = 1
				cb = 0
				ind += 1
				while (ind < strlen) :
					if (program[ind] == '[') :
						ob += 1
					elif (program[ind] == ']') :
						cb += 1
					elif (program[ind] == '\n') :
						lineno += 1
					if (cb == ob) :
						break
					ind += 1

				if(ob != cb) :
					Q.put(f"SYNTAX ERROR : Line {lineno}")
					return
		elif (program[ind] == ']') :
			if (len(brackets) == 0) :
				Q.put(f"SYNTAX ERROR : Line {lineno}")
				return
			if (data[ptr] == 0) :
				brackets.pop()
			else :
				lineno = brackets[-1][1]
				ind = brackets[-1][0]
		elif (program[ind] == '\n') :
			lineno += 1
		ind += 1

	if (len(brackets) != 0) :
		Q.put(f"SYNTAX ERROR : Line {lineno}")
		return

	with open(outputPath,'w+') as f :
		f.write(out_buff)

	Q.put("ANSWER WRITTEN")
	return
