"""
An edited source code.

Demo of Gale-Shapley stable marriage algorithm. 
Original Code at:
http://cs.slu.edu/~goldwasser/courses/slu/csci314/2006_Spring/lectures/marriageAlgorithm/

What is changed by lovebes:
Edited to be in polyandry mode, by lovbes
Also accounts for special to special sub group matching. Special husbands can ONLY go into special wives.

Usage is:
   python matching.py  [studentsChoice] [sitesRank] [sitesCapacity] [siteTypes] [specStudentList]

or   

   python marriage_addEilat.py  studentsChoice sitesRank sitesCapacity siteTypes specStudentList V

for verbose mode.   

and likewise for the womenfile, where there should be precisely same
number of men as with women, and the identifiers should be
self-consistent between the two files.



"""
import sys


class Person:
    """
    Represent a generic person
    """
    def __init__(self,name,priorities):
        """
        name is a string which uniquely identifies this person

        priorities is a list of strings which specifies a ranking of all
          potential partners, from best to worst
        """
        self.name = name
        self.priorities = priorities
        self.partner = None

    def __repr__(self):
        return 'Name is ' + self.name + '\n' + \
               'Partner is currently ' + str(self.partner) + '\n' + \
               'priority list is ' + str(self.priorities)


class Man(Person):
    """
    Represents a man
    """
    def __init__(self,name,priorities,specialList):
        """
        name is a string which uniquely identifies this person

        priorities is a list of strings which specifies a ranking of all
          potential partners, from best to worst
        """
        Person.__init__(self,name,priorities)
        # flag if name matches name in specialList
        self.myType = "normal"
        for special in specialList: # name = each of the stored special sites - eg 'B7', 'Eilat'
            typeOf = special[0]            
            for site in special[1]:        
                if self.name == site: 
                    self.myType = typeOf
                    

        for name in specialList:
            if self.name == name:
                self.amSpecial = True
                print self.name+' is special'

        self.proposalIndex = 0                   # next person in our list to whom we might propose

    def nextProposal(self):
        goal = self.priorities[self.proposalIndex]
        self.proposalIndex += 1
        return goal

    def __repr__(self):
        return Person.__repr__(self) + '\n' + \
               'next proposal would be to ' + self.priorities[self.proposalIndex]
            

class Woman(Person):
    """
    Represents a woman
    """
    def __init__(self,name,priorities,husbandReq,specialList,specHubbyList):
        """
        name is a string which uniquely identifies this person

        priorities is a list of strings which specifies a ranking of all
          potential partners, from best to worst
        """
        Person.__init__(self,name,priorities)
        # store the type if name matches name in specialList, else: "normal"
        self.myType = "normal"
        for special in specialList: # name = each of the stored special sites - eg 'B7', 'Eilat'
            typeOf = special[0]            
            for site in special[1]:        
                if self.name == site: 
                    self.myType = typeOf
                    
        self.specHubbyArr = specHubbyList #maintain list of hubbies that you need to take!!
        # now compute a reverse lookup for efficient candidate rating
        self.ranking = {}
        for rank in range(len(priorities)):
            self.ranking[priorities[rank]] = rank

        self.evenDenyArr = [] #list of hubby not to add if want to make even hubbys (even Male, even Female)

	self.husbands = int(husbandReq) #will be populated by file

	self.husbandsArr = [] #limit by self.husbands. Array of int that are index values of priorities array.

    def eqHubbyType(self, hubby, typeHubby): #check if hubby is of type typeHubby. Return false/true
        for hubbyType in self.specHubbyArr:
            if hubbyType[0] == typeHubby:
                for h in hubbyType[1]:
                    if hubby == h:
                        return True
        return False
            

    def evaluateProposal(self,suitor):
        """
        Evaluates a proposal, though does not enact it.

        suitor is the string identifier for the man who is proposing

        returns True if proposal should be accepted, False otherwise
        """
        #checking  B7 types:
            # if wife is not 'B7' type, hubby is 'B7' type : just say no!!
        if self.eqHubbyType(suitor, 'B7') and self.myType != "B7": #hubby is 'B7'
                return False

        #normal comparison
        if len(self.husbandsArr) == self.husbands: #if husbandsArr full, see if suitor is a better match.
            count = 0
            for hubby in self.husbandsArr:#hubby is integer for priorities. Can use it to compare ranking. Lower # == better suitor
                if self.ranking[suitor] < hubby:
                    count += 1
 
            #checking Eilat types: if the person is in the blacklist, deny adding person to hubbyArr
                '''            
                if self.myType == "Eilat" and count > 0:

                #if counting suitor + husbandsArr(minus last one) is even, then we call this "will get even" == true
           
                futureHubArr = list(self.husbandsArr)
                futureHubArr.pop()
                futureHubArr.append(self.ranking[suitor])
                print str(self.husbandsArr)+":"+str(futureHubArr) 
                return self.isEvenHubArr(futureHubArr) #algorithm wrong. Currently men runs out of choice.
                '''                
#                return self.isEvenHubArr() 
            #check B7. If not a good suitor, but B7, just say yes and invoke inclusion/bumping of last one:
            if self.myType == "B7" and self.eqHubbyType(suitor,'B7') and count == 0:
                return True
            return count > 0

	    #if husbandsArr not full, just say yes.
        return len(self.husbandsArr) < self.husbands 

    def isEvenHubArr(self):
        count = 0
        for hubby in self.husbandsArr: #hubby is an integer.
            hubbyName = self.priorities[hubby]
            for hubbyType in self.specHubbyArr:
                if hubbyType[0] == "Male": #gotta check for this
                    for h in hubbyType[1]:
                        if h == hubbyName:
                            count += 1
        return count%2 == 0 #True if even.

    def husbandsFull(self):
        return len(self.husbandsArr) == self.husbands

    def addHubby(self,hubbyName):
        self.husbandsArr.append(self.ranking[hubbyName])
        self.husbandsArr.sort()

    def addEvenDeny(self,hubbyName):#used for Eilat
        self.evenDenyArr.append(self.ranking[hubbyName])
        self.evenDenyArr.sort()

    def popHubby(self):
        #return name of popped hubby

        if self.myType == "B7":
            #goal: pop only non-B7 
            #1. reverse list
            rev = list(self.husbandsArr)
            rev.reverse() #it works because list is already sorted by rank
            #2. for loop check if hubby is B7. Scan until find non-B7 hubby. Pop that!
            name = ''
            for num in rev:
                if not self.eqHubbyType(self.priorities[num],'B7'):
                    rev.remove(num)
                    name = self.priorities[num]
                    break
            rev.reverse()
            self.husbandsArr = list(rev)
            return name
        else:
            popped = self.husbandsArr.pop()         
            return self.priorities[popped]



def parseFile(filename):
    """
    Returns a list of (name,priority) pairs.
    """
    people = []
    f = file(filename)
    for line in f:
        pieces = line.split(':')
        name = pieces[0].strip()
        if name:
            priorities = pieces[1].strip().split(',')
            for i in range(len(priorities)):
                priorities[i] = priorities[i].strip()
            people.append((name,priorities))
    f.close()

    return people

def parseFile2(filename):
    """
    Populates how many husbands one wife needs.
    Returns a list of (wife,numHusband) pairs.
    """
    wives = []
    f = file(filename)
    for line in f:
        pieces = line.split(':')
        name = pieces[0].strip()
        if name:
            husbands = pieces[1].strip()
            wives.append((name,husbands))
    f.close()
    return wives

def parseFile3(filename): #<_________NOT USED BY ANYONE
    #get the comma-delimited one line info of either special husbands and special wives

    f = file(filename)
    arr = f.readline().strip().split(',')
    f.close()
    return arr
    

def printPairings(men):
    for man in men.values():
        print man.name,'is paired with',str(man.partner)

def printPairings2(menArr):
    newArr = []	
    for man in menArr:
        #print man[1].name.ljust(10,' '),str(man[1].partner),'\tno '+str(man[1].proposalIndex)+' in preference'
        newArr.append([man[1].name,str(man[1].partner),man[1].proposalIndex])
    newArr.sort(key=lambda x: x[1])
    for man in newArr:
        print "Site: "+man[1].ljust(10,' ')+man[0].ljust(10,' ')+str(man[2])+" in preference"

def printPairings3(womenArr,men, doCSV):
    newArr = []	
    for woman in womenArr:
        #print man[1].name.ljust(10,' '),str(man[1].partner),'\tno '+str(man[1].proposalIndex)+' in preference'
        partArr = []
        for hubby in woman[1].husbandsArr:
            partArr.append([woman[1].name,woman[1].priorities[hubby],hubby, men[woman[1].priorities[hubby]].proposalIndex])
        partArr.sort(key=lambda x: x[2])
        newArr.append(partArr)
    if not doCSV:
        for woman in newArr:
            for hubby in woman:
                print "Site: "+hubby[0].ljust(10,' ')+hubby[1].ljust(10,' ')+str(hubby[2]+1).ljust(3,' ')+"in Site's preference, "+str(hubby[3])+" in Student's preference"
    else:
        f = file('matched.csv','w')
        for woman in newArr:
            for hubby in woman:
                f.write(hubby[0]+','+hubby[1]+','+str(hubby[2]+1)+" in Site's preference, "+str(hubby[3])+" in Student's preference"+'\n')
        f.close()
        

    
def dict2Arr(dictionary):
	dictlist = []
	for key, value in dictionary.iteritems():
	    temp = [key,value]
	    dictlist.append(temp)
	return dictlist


if __name__=="__main__":
    verbose = len(sys.argv)>6
    # get a list of the special condition husbands that can only match to special wives. arg #5
    specHubbyArr = parseFile(sys.argv[5])

    # get a list of special sites #4 - type and siteArray dictionary.
    specWivesArr = parseFile(sys.argv[4])

    # initialize dictionary of men
    menlist = parseFile(sys.argv[1])
    men = dict()
    for person in menlist:
        men[person[0]] = Man(person[0],person[1],specHubbyArr)
    unwedMen = men.keys()
    
    # initialize dictionary of women
    womenlist = parseFile(sys.argv[2])
    husbandReqs = parseFile2(sys.argv[3])
    dictOne = dict(womenlist)
    dictTwo = dict(husbandReqs)
    combined = dict()
    for name in set(dictOne.keys() + dictTwo.keys()):
        combined[name] = [dictOne.get(name,0), dictTwo.get(name,0)]
    combinedWomen = []
    for name in combined:
        combinedWomen.append([ name ] + combined[name])

    women = dict()
    for person in combinedWomen:
        women[person[0]] = Woman(person[0],person[1],person[2],specWivesArr,specHubbyArr)

    doEvenHubby = True
    ############################### the real algorithm ##################################
    while unwedMen:
        m = men[unwedMen[0]]             # pick arbitrary unwed man
        w = women[m.nextProposal()]      # identify highest-rank woman to which
                                         #    m has not yet proposed
        if verbose:  print m.name,'proposes to',w.name

        if w.evaluateProposal(m.name):#means m.name is better match
            if verbose: print '  ',w.name,'accepts the proposal'
            
            if w.husbandsFull():
                # last hubby in hubbyArr is dumped, as that is least suitable
                mOld = men[w.popHubby()]
                mOld.partner = None
                unwedMen.append(mOld.name)
                
                # then add the new man
                w.addHubby(m.name)
                unwedMen.remove(m.name)
                m.partner = w.name
                '''
                if w.myType == "Eilat" and len(unwedMen) == 0: #all filled up. Now gotta check if this is even..
                    if not w.isEvenHubArr(): #TODO: add the person to blacklist, reset/run again entire while loop
                                            #or - just remove the person, forcing while loop to run again with m's next proposal..
                        mOld = men[w.popHubby()]
                        mOld.partner = None
                        unwedMen.append(mOld.name)                        
                        
                '''
            else:	
                #if not full, and a nice suitor, just add him to the pack

                unwedMen.remove(m.name)
                w.addHubby(m.name)
                m.partner = w.name
        else:
            if verbose: print '  ',w.name,'rejects the proposal'




            
        if verbose:
            print "Tentative Pairings are as follows:"
            printPairings(men)
            print

    #####################################################################################
    menArr = dict2Arr(men)
    menArr.sort(key=lambda x: x[0])
    womenArr = dict2Arr(women)
    womenArr.sort(key=lambda x: x[0])
 
    # we should be done
    print "Final Pairings are as follows:"
    printPairings2(menArr)
    printPairings3(womenArr,men, True)
