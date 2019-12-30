#include<iostream>
#include<stack>
#include<string.h>
#include<utility>
#include<fstream>

#define MAX_SIZE 1e6
#define MAX_CELLS 65536
#define MAX_VAL 255
#define MIN_VAL 0

using namespace std;

int lineno = 1;
unsigned char data[MAX_CELLS] = {0};
int ptr = 0;
stack<pair<int,int> > brackets;

string inp_buff = "",out_buff = "";
int inp_ind = 0;

int interpret(string &program,int start = 0){
	int ind = start;
	while(program[ind] != EOF){
		if(program[ind] == '+'){
			if(data[ptr] >= MAX_VAL) data[ptr] = MIN_VAL;
			else data[ptr]++;
		}
		else if(program[ind] == '-'){
			if(data[ptr] <= MIN_VAL) data[ptr] = MAX_VAL;
			else data[ptr]--;
		}
		else if(program[ind] == '<'){
			ptr--;
			if(ptr < 0) ptr = MAX_CELLS-1;
		}
		else if(program[ind] == '>'){
			ptr++;
			if(ptr >= MAX_CELLS) ptr = 0;
		}
		else if(program[ind] == ','){
			if(inp_ind >= inp_buff.length()){
				cout<<"RUNTIME ERROR : No Input Character for Line "<<lineno<<endl;
				return 0;
			}
			data[ptr] = inp_buff[inp_ind++];
		}
		else if(program[ind] == '.'){
			out_buff += data[ptr];
		}
		else if(program[ind] == '['){
			if(data[ptr] != 0){
				brackets.push(make_pair(ind,lineno));
				ind++;
				continue;
			}
			int ob = 1,cb = 0,p_lineno = lineno;
			while(program[++ind] != EOF){
				if(program[ind] == '[') ob++;
				else if(program[ind] == ']') cb++;
				else if(program[ind] == '\n') lineno++;
				if(cb == ob) break;
			}
			if(ob != cb){
				cerr<<"SYNTAX ERROR : Corresponding Closing Brackets not found for Line "<<p_lineno<<endl;
				return 0;
			}
		}
		else if(program[ind] == ']'){
			if(brackets.size() == 0){
				cerr<<"SYNTAX ERROR : Corresponding Opening Brackets not found for Line "<<lineno<<endl;
				return 0;
			}
			if(data[ptr] == 0){
				brackets.pop();
				ind++;
				continue;
			}
			lineno = brackets.top().second;
			ind = brackets.top().first;
		}
		else if(program[ind] == '\n'){
			lineno++;
		}
		ind++;
	}
	if(brackets.size()) {
		cerr<<"SYNTAX ERROR : Brackets not matching"<<endl;
		return 0;
	}
	return 0;
}

int main(int argc,char **argv){
	string input(argv[2]),output(argv[3]);
	string source(argv[1]);

	ifstream fsource(source.c_str());

	ifstream fin(input.c_str());
	ofstream fout(output.c_str());

	if(fin == NULL || fout == NULL || fsource == NULL){
		cout<<"FILE ERROR : Error while opening files"<<endl;
		return 0;
	}

	string program = "";
	string tmp;
	long long noi = 0;
	while(getline(fsource,tmp)){
		noi += tmp.length();
		program += tmp;
		program += "\n";
	}
	program += EOF;

	if(noi > MAX_SIZE){
		cout<<"MEMORY ERROR : Number of Instructions exceeded the Maximum Limit"<<endl;
		return 0;
	}

	while(fin>>tmp){
		inp_buff += tmp;
	}

	interpret(program);

	//out_buff += EOF;
	fout.write(out_buff.c_str(),out_buff.length());

	fin.close();
	fout.close();
	fsource.close();

	return 0;
}