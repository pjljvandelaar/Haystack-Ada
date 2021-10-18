#from tmp2 import *
import tmp2
# Inizializing the program and the vars:
tmp2.createHashMap()

list = tmp2.returnSlock()
list = (tmp2.startEnd(list))
print("Slock Ranges found: "+str(list))


def writeNewLine():
    while(int(input("Enter 1 if you want to add a NewLine, if not something else: ")) == 1):
        startend = []
        f = open("helloWorld.adb", "r")
        contents = f.readlines()
        f.close()
        index = int(input("Insert the index line that you want to replace: ")) 
        # index = index -1
        string = str(input("Insert what do you want to insert: ")+"\n")
        # Need to find the first char in order to indentate well the code
        for subList in list:
            if(subList[0] == index):
                startend.append(subList[1])
            else:
                startend.append(None)
        print(startend)
        res = []
        toChange = ""
        for val in startend:
            if val != None :
                res.append(val)
        if(len(res) == 0):
            res.append(None)
        start = res[0]
        print("Start char : "+ str(start))
        if(start == None):
            toChange = string
        else:
            for i in range(start):
                toChange = toChange + " "
            # toChange = contents[index]
            print(toChange)
            toChange = toChange[0:start-1] + string 
            print(toChange)
        '''if(len(contents) < index):
            contents[index] = "Trying to add after"      What about a index that is not in the file?
            f = open("helloWorld.adb", "w")
            f.writelines(contents)
        else: '''
        contents.insert(index, toChange)
        f = open("helloWorld.adb", "w")
        contents = "".join(contents)
        f.write(contents)
        f.close()

writeNewLine()