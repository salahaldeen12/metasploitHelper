import commands
import re
import argparse
import sys

path = "/pentest/metasploit-framework/modules"

def lookupPort(matchPort):
	print "\n- Modules Matching Port: "+str(matchPort)+"\n"

	fullCmd = 'grep -ir "Opt::RPORT" '+path
	results =  RunCommand(fullCmd)
	portList=[]
	lookupList=[]
	exploitList=[]
	resultsList = results.split("\n")
	for result in resultsList:
		result1 = result.split(".rb:")[1].strip()
		exploitModule = result.split(".rb:")[0].strip()+".rb"
		portNo = find_between(result1,"RPORT(",")")
		if not any(c.isalpha() for c in portNo):
			if len(matchPort)>0:
				if portNo==matchPort:
					lookupList.append([exploitModule,portNo])
			if portNo not in portList:
				portList.append(portNo)
			if "fuzzer" not in exploitModule and "auxiliary/dos" not in exploitModule:
				exploitList.append([exploitModule,portNo])

	for x in lookupList:
		lines=[]
		filename = x[0]
		if "fuzzer" not in filename:
			print filename
			#print filename+"\t"+x[1]
			with open(filename) as f:
				lines = f.read().splitlines()
			startFound=False
			optionList=[]
			found=False
			tempStrList=[]
			finalList=[]
			for line in lines:
				if "register_options" in line:
					startFound=True
				if "self.class)" in line and found==False:
					found1=False
					for y in optionList:
						if found1==True:
							y = y.strip()
							if "#" not in y:
								tempStrList.append(y)
						if ".new" in y:
							if found1==True:
								tempStrList=[]
								found1=False
							if "[" in y and "]" in y:
								y = y.strip()
								finalList.append(y)
							else:
								y = y.strip()
								if "#" not in y:
									tempStrList.append(y)
									found1=True
					startFound=False
					found=True
				if startFound==True:
					optionList.append(line)
			result1=""
			for y in tempStrList:
				try:	
					m = re.search('"(.+?)"',y)
					temp1 = str(m.group(1)).replace(",","")
					y = y.replace(m.group(1),temp1)
					result1 += y
				except AttributeError:
					result1 += y
					continue
			if len(str(result1))>0:
				finalList.append(result1)
			tempStr1=""
			for g in finalList:
				if "false" not in g.lower() and "rhost" not in g.lower():
					parameterList = g.partition('[')[-1].rpartition(']')[0]
					parNameTemp =( g.split(",")[0]).partition("'")[-1].rpartition("'")[0]
					result = (parameterList.split(",")[-1]).strip()
					if result=='""' or result=="''":
						tempStr1+= parNameTemp
						tempStr1+= ","
			if len(tempStr1)>0:
				if tempStr1[-1]==",":
					print "- Variables required for module: "+tempStr1[0:(len(tempStr1)-1)]
def lookupURI(showModules=False):
	path = "/pentest/metasploit-framework/modules"
	#fullCmd = 'grep -ir "Opt::RPORT" '+path
	fullCmd = 'grep -ir "OptString.new(\'TARGETURI\'" '+path
	results =  RunCommand(fullCmd)
	exploitList=[]
	pathList=[]
	uriList=[]
	defaultPathList=[]
	resultsList = results.split("\n")
	for result in resultsList:
		result1 = result.split(".rb:")[1].strip()
		exploitModule = result.split(".rb:")[0].strip()+".rb"
		portNo = find_between(result1,"[","]")
		if "fuzzer" not in exploitModule and "auxiliary/dos" not in exploitModule:
			exploitList.append([exploitModule,portNo])
			result1 = portNo.split(",")[-1]
			result1 = result1.replace("'","")
			result1 = result1.replace('"',"")
			result1 = result1.strip()
			if "/" in result1:
				if result1!="/":
					if result1 not in uriList:
						uriList.append(result1)
				if result1=="/":
					defaultPathList.append([result1,exploitModule])
				else:
					if result1 not in pathList:		
						pathList.append([result1,exploitModule])
	if showModules==False:
		for x in uriList:
			print x
	else:
		for x in pathList:
			print x[0]+","+x[1]
		for x in defaultPathList:	
			print x[0]+","+x[1]

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def RunCommand(fullCmd):
    try:
        return commands.getoutput(fullCmd)
    except:
        return "Error executing command %s" %(fullCmd)

if __name__ == '__main__':
	print "This tool parses Nmap XML file and checks for matching ports/exploits in Metasploit"
	print "The tool will print out if there any additional parameters that needs to be supplied to the Metasploit module."
	parser = argparse.ArgumentParser()
    	parser.add_argument('-uri', action='store_true', help='[shows targetURI from metasploit modules]')
    	parser.add_argument('-uriModules', action='store_true', help='[shows targetURI and modules from metasploit modules]')
    	parser.add_argument('-port', dest='portNo',  action='store', help='[Port Number]')

    	if len(sys.argv)==1:
        	parser.print_help()
        	sys.exit(1)
	options = parser.parse_args()
	showModules=False
	if options.uri:
		lookupURI(showModules=False)
	if options.uriModules:
		lookupURI(showModules=True)
	if options.portNo:
		lookupPort(options.portNo)
   