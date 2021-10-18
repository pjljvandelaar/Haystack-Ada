# Do a replace of a HelloWorld in ADA language:
import libadalang as lal
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument('--project', '-P', type=str)
parser.add_argument('files', help='Files to analyze', type=str, nargs='+')
args = parser.parse_args()

provider = None
if args.project:
    provider = lal.UnitProvider.for_project(args.project)
context = lal.AnalysisContext(unit_provider=provider)

data = dict()
slock_range = []

for filename in args.files:
    unit = context.get_from_file(filename)
    print("==== {} ====".format(filename))
    for d in unit.diagnostics:
        print("{}: {}".format(filename, d))
    print("All If statement in : {}".format(filename))
    for call in unit.root.findall(lal.IfStmt):
        print("--> Line {}: {}".format(call.sloc_range.start.line, repr(call.text)))
        # data.update({str(call.sloc_range):call.text})
        # slock_range.append(str(call.sloc_range))
        for child in call.children:
                if(child != None):
                    if(child.text == ''):
                        pass
                    else:
                        data.update({str(child.sloc_range):child.text})
                        slock_range.append(str(child.sloc_range)) 
    for call in unit.root.findall(lal.ElsifExprPartList):
        print("--> Line {}: {}".format(call.sloc_range.start.line, repr(call.text)))
        # data.update({str(call.sloc_range):call.text})
        # slock_range.append(str(call.sloc_range))
        for child in call.children:
                if(child != None):
                    if(child.text == ''):
                        pass
                    else:
                        data.update({str(child.sloc_range):child.text})
                        slock_range.append(str(child.sloc_range))    
    print("Data: "+ str(data))   
    print("Slock_range: "+str(slock_range))