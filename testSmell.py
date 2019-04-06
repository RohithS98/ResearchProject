import subprocess
import os
from collections import defaultdict as dd
import pickle
					
def compress(op):
	d = dd(int)
	op = op.split('\n')
	for i in op:
		t = i.split()
		if not t:
			continue
		if t[1] == 'Local' and t[-1] == 'final':
			d['locFinal'] += 1
		elif t[1] == 'Avoid' and t[-1] == 'loops':
			d['loopObj'] += 1
		elif len(t) > 3 and t[1] == 'This' and t[2] == 'final' and t[-1] == 'static':
			d['finToStat'] += 1
		elif len(t) > 3 and t[1:5] == ['Avoid','empty','catch','blocks']:
			d['catchEmp'] += 1
		elif len(t) > 4 and t[-1] == 'String' and t[-2] == 'blank':
			d['blankStr'] += 1
		elif len(t) > 5 and t[1] == 'Avoid' and t[3] == 'toString()':
			d['toString'] += 1
		elif len(t) > 4 and t[1] == 'Do' and t[-2] == 'empty' and t[-1] == 'string':
			d['addEmptyStr'] += 1
		elif len(t) > 4 and t[1] == 'Avoid' and t[2] == 'appending':
			d['appendChar'] += 1
		elif len(t) > 3 and t[1:5] == ['Avoid','empty','finally','blocks']:
			d['finallyEmp'] += 1
		elif len(t) > 5 and t[1] == 'Dont' and t[2] == 'call' and t[3] == 'Thread.run()':
			d['threadRun'] += 1
		else:
			pass
	return d
		
 
baseCMD = ["pmd-bin-6.13.0/bin/run.sh","pmd","-R",
					   "androidSmells.xml","-f","text","-d"]

fPrefix = "dataset/"
files = os.listdir(fPrefix)
files.sort()
fileList = list(map(lambda x : fPrefix + x, files))

smellDict = dict()

for i in fileList:
#for i in ['dataset/pipepanic-android']:
	p1 = subprocess.Popen(baseCMD + [i],stdout = subprocess.PIPE)
	op, err = p1.communicate()
	print(i)
	smellDict[i] = compress(op.decode('utf-8'))

'''
f = open('smellOutput.bin','wb')
pickle.dump(smellDict,f)
f.close()
'''

check = os.path.isfile('smellOP.csv')
if check:
	print('\nAdding to existing file\n')
	f = open('smellOP.csv','a')
else:
	print('\nCreating new file\n')
	f = open('smellOP.csv','w')
	f.write('Name,AvoidInstantiationInLoop,LocalCouldBeFinal,FinalCouldBeStatic,'+
'EmptyCatch,InefficientEmptyString,StringToString,AddEmptyString,AppendingCharacter'+
'WithChar,EmptyFinally,ThreadRun\n')

for i in smellDict:
	f.write(i+',')
	for j in ['loopObj','locFinal','finToStat','catchEmp','blankStr','toString',
			'addEmptyStr','appendChar','finallyEmp','threadRun']:
		f.write(str(smellDict[i][j]))
		if j != 'threadRun':
			f.write(',')
	f.write('\n')
f.close()
