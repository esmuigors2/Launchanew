#!/usr/bin/python

import sys, getopt, re, os
print(sys.version)
if os.isatty(sys.stdout.fileno()) : 
    buzzing = True 
    try:
        termcolumns = int(os.get_terminal_size().columns)
    except:
        termcolumns = int(os.popen('stty size', 'r').read().split()[1])
else : 
    buzzing = False
avaispac = 3 # will be modified later

# threshold for recognizing the almost converged state
zerothresh = 2.0

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   DARKBLUE = '\033[34m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   DIM = '\033[2m'
   HIDDEN = '\033[8m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

def fmso_usage():
    if buzzing : print('Usage:\nfindminstep filename [filename2 filename3 ...]\nOther options:\n ' + color.BOLD + '-j INT/--job=INT ' + color.END + ': select the job within the file\n ' + color.BOLD + '-s/--steps ' + color.END + ': printing of all steps\n ' + color.BOLD + '-b/--beststeps ' + color.END + ': printing of steps deemed best (usualy MORE than one)\n ' + color.BOLD + '-i INT/--strictness=INT ' + color.END + ': how strict to be when detecting cycling (smaller = stricter, may conclude that the whole optimization is rubbish; default = 3)\n ' + color.BOLD + '-n INT/ -normalize-to=INT ' + color.END + ': normalize convergence criteria to Normal (1, default), Tight (2, default if Opt=Tight is found within the job) or VeryTight (3, default if Opt=VeryTight is found within the job)\n ' + color.BOLD + '-x/--scpcm ' + color.END + ': find the best step of SC-PCM instead (x for eXtra)\n ' + color.BOLD + '-v/--verbose ' + color.END + ': same as -s (used for compatibility).')

def normsteps(s,t,u):
    try:
        return round(float(s)/float(t),5)
    except ValueError:
        return u

# defining the nstep to use it in getbestst()
nstep = 0

def getbestst(y,nstep):
    #print('NStep is currently ',nstep)
    x = list(y) # in python, lists are passed by ref
    w = []
    t = 0
    if x[0] > 0:
        criter = round(2*min(x),5)
    else:
        criter = round(min(x)+0.0001*(max(x)-min(x)),5)
    try:
        z=sorted(zip(x,xrange(0,len(x))), key=lambda sorrow: sorrow[0])
    except NameError:
        z=sorted(list(zip(x,range(0,len(x)))), key=lambda sorrow: sorrow[0])
#    print("Criyter is "+str(criter))
 #   print("Length of z is "+str(len(z)))
    while z[t][0] <= criter:
  #      print("Z["+str(t)+"][0] is:"); print(z[t][0])
        if z[t][1] < nstep:
            w.append(z[t][1]+1)
        t += 1
        if t == len(z): break
    return list(w)

def crudecycle(unisteps):
#    print("###y: ")
#    print(y)
    y = [ yy for yy in unisteps if yy > zerothresh ]#set(unisteps)
#    print("The list passed to the crudecycle:"); print(y)
    leny = round(len(y)/2)
    alarmed = 100500
    repe = [ [ k for k, v in enumerate(y) if v == vaa ] for vaa in y ]
# "repe" is a list of lists of repeating steps
#    repen = [ vaa for vaa in y ]
#    print("###Repe: ")
#    print(repe)
    try:
        repesteps = dict(zip(xrange(0,len(y)),repe))
    except NameError:
        repesteps = dict(list(zip(range(0,len(y)),repe)))
#    print("###Repesteps: ")
#    print(repesteps)
    for u in list(repesteps):
        if len(repesteps[u]) > 2:
# if some list of repeating steps contains more than two steps and the step number is less
# than the current "alarmed" the last is assigned this new, lower step number (after which
# the cycling becomes possible
            if len(repesteps[u]) <= leny: alarmed = int(min([ baa+1 for baa in repesteps[u] ]+[int(alarmed)]))
            #print("List of which min is computed:");print(repesteps[u]+[int(alarmed)])
            #print("Alarmed is now "+str(alarmed))
        #else:
            #print("this is a healthy step")
    if alarmed < 10050:
        return alarmed # crudely determined start of cycling, more precisely with bisection?
    else:
        return 0

# SHA-A-A-AMEFUL PIECE OF CODE O(N^2)
#def thoroughcycle(y):
#    #[ yy for yy in y if yy > 0.0 ])
#    h = [ yy for yy in y if yy > zerothresh ]
#    repe = [ [ k for k, v in enumerate(h) if v == vaa ] for vaa in h ]
#    repesteps = dict(zip(xrange(0,len(h)),repe))
##    print("###Repesteps: ")
##    print(repesteps)
##    print(repe)
#    maxtelen = 1
#    for u in list(repesteps):
#        if len(repesteps[u]) > maxtelen:
#            maxtelen = len(repesteps[u])
#    return maxtelen

def thoroughcycle(y):
    #[ yy for yy in y if yy > 0.0 ])
    h = [ yy for yy in y if yy > zerothresh ]
    repe = set(h)
    maxtelen=1
    if len(h) > len(repe):
        for u in repe:
            hcu = h.count(u)
            if hcu > maxtelen:
                maxtelen = hcu
    return maxtelen


def smuk(gar):
    if avaispac > 4:
        return 14
    else:
        return gar+avaispac

def outputscpcmsteps(pa,cavi,en,av,ae,ma,ac2=[],ac3=[],ac4=[],ac5=[],ac6=[]):
    print('\n-----------------Job steps-----------------')
    global avaispac
    avaispac=round((termcolumns-53)/4) # -53 = -4-10-12-11-16 ; previously the first 10 was 12
    myveryowndesignheader='%-4s%'+str(smuk(10))+'s%'+str(smuk(12))+'s%'+str(smuk(11))+'s%'+str(smuk(16))+'s'
    print(myveryowndesignheader % ('Step','RMS_dE_x_100','Max_dE_x_10','Avrge_x_100','Mov.av.(3)_x_100'))
    try:
        for mt in xrange(0,cavi):
            f1 = f6 = f7 = f8 = '.4e'
            if en[mt] < 1000: f1 = '.5f'
            if av[mt] < 1000: f6 = '.5f'
            if ae[mt] < 1000: f7 = '.5f'
            if ma[mt] < 1000: f8 = '.5f'
            myveryowndesignheaderm='%-4d%'+str(smuk(10))+f1+'%'+str(smuk(12))+f6+'%'+str(smuk(11))+f7+'%'+str(smuk(16))+f8
            print(myveryowndesignheader % ((mt+1), (en[mt]*100), (av[mt]*10), ae[mt]*100, (ma[mt]*100)))
    except NameError:
        for mt in range(0,cavi):
            f1 = f6 = f7 = f8 = '.4e'
            if en[mt] < 1000: f1 = '.5f'
            if av[mt] < 1000: f6 = '.5f'
            if ae[mt] < 1000: f7 = '.5f'
            if ma[mt] < 1000: f8 = '.5f'
            myveryowndesignheaderm='%-4d%'+str(smuk(10))+f1+'%'+str(smuk(12))+f6+'%'+str(smuk(11))+f7+'%'+str(smuk(16))+f8
            print(myveryowndesignheader % ((mt+1), (en[mt]*100), (av[mt]*10), ae[mt]*100, (ma[mt]*100)))


def outputsteps(pa,cavi,en,mf,rf,ms,rs,av,ae,ma,ac2=[],ac3=[],ac4=[],ac5=[],ac6=[]):
    print('\n-----------------Job steps-----------------')
    global avaispac
    avaispac=int((termcolumns-85)/8) # 85 = 4 + 10 + 6 x 10 + 11 ; previously the first 10 was 12
    if avaispac <= 0: avaispac = 0
    fstri='%-4s%'+str(smuk(10))+'s%'+str(smuk(10))+'s%'+str(smuk(10))+'s%'+str(smuk(10))+'s%'+str(smuk(10))+'s%'+str(smuk(10))+'s%'+str(smuk(10))+'s%'+str(smuk(11))+'s'
    print(fstri % ('Step','Energy','Max Force','RMS Force','Max Displ','RMS Displ','Average','Avrg+E','Mov.av.(3)'))
    #print('%-4s%'+str(smuk(12))+'s%'+str(smuk(10))+'s%'+str(smuk(10))+'s%'+str(smuk(10))+'s%'+str(smuk(10))+'s%'+str(smuk(10))+'s%'+str(smuk(10))+'s%'+str(smuk(11))+'s' % ('Step','Energy','Max Force','RMS Force','Max Displ','RMS Displ','Average','Avrg+E','Mov.av.(3)'))
    #print('Avaispac is '+str(avaispac))
    try:
        for mt in xrange(0,cavi):
            f1 = f2 = f3 = f4 = f5 = f6 = f7 = f8 = '.4e'
            if en[mt] < 1000: f1 = '.5f'
            if mf[mt] < 1000: f2 = '.5f'
            if rf[mt] < 1000: f3 = '.5f'
            if ms[mt] < 1000: f4 = '.5f'
            if rs[mt] < 1000: f5 = '.5f'
            if av[mt] < 1000: f6 = '.5f'
            if ae[mt] < 1000: f7 = '.5f'
            if ma[mt] < 1000: f8 = '.5f'
            fstri='%-4d%'+str(smuk(10))+f1+'%'+str(smuk(10))+f2+'%'+str(smuk(10))+f3+'%'+str(smuk(10))+f4+'%'+str(smuk(10))+f5+'%'+str(smuk(10))+f6+'%'+str(smuk(10))+f7+'%'+str(smuk(11))+f8
            print(fstri % (mt+1, en[mt], mf[mt], rf[mt], ms[mt], rs[mt], av[mt], ae[mt], ma[mt]))
    except NameError:
        for mt in range(0,cavi):
            f1 = f2 = f3 = f4 = f5 = f6 = f7 = f8 = '.4e'
            if en[mt] < 1000: f1 = '.5f'
            if mf[mt] < 1000: f2 = '.5f'
            if rf[mt] < 1000: f3 = '.5f'
            if ms[mt] < 1000: f4 = '.5f'
            if rs[mt] < 1000: f5 = '.5f'
            if av[mt] < 1000: f6 = '.5f'
            if ae[mt] < 1000: f7 = '.5f'
            if ma[mt] < 1000: f8 = '.5f'
            fstri='%-4d%'+str(smuk(10))+f1+'%'+str(smuk(10))+f2+'%'+str(smuk(10))+f3+'%'+str(smuk(10))+f4+'%'+str(smuk(10))+f5+'%'+str(smuk(10))+f6+'%'+str(smuk(10))+f7+'%'+str(smuk(11))+f8
            print(fstri % (mt+1, en[mt], mf[mt], rf[mt], ms[mt], rs[mt], av[mt], ae[mt], ma[mt]))
    
    print("If the output is too cluttered, please expand the terminal window")


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
# this one is (c) Daniel Goldberg at so.com

def main():
    printsteps = False
    printbeststeps = False
    printacs = False
    helps = False
    cystrict = 3
    myjob = 0
    normalizeto = 0 # default which is thus defferentiable from the manual choice of normal criteria
    doscpcmconv = False
    njobslist = []
    njobslist1 = []
    energias = []
    energias1 = []
    denergias = []
    rmsdispl = []
    maxdispl = []
    rmsforce = []
    maxforce = []
    nstep = 0
    exitstat = 0

# this is the formatting to three significant digits (c) Peter Graham @ so.com
    roundstr='%.'+str(cystrict)+'g'
    
    try:
        opts, restargs = getopt.getopt(sys.argv[1:], "hi:xsbn:j:v", ["help", "steps", "scpcm", "beststeps", "strictness=", "normalize-to=", "job=", "verbose"])

    except getopt.GetoptError:        # no "as" clause in python 2.2
        # print help information and exit:
        if buzzing : print("Some option was not recognized.")  # will print something like "option -a not recognized"
        fmso_usage()
        sys.exit(2)
    verbose = False
    for o, a in opts:
        if o in ("-v", "--verbose"):
            printsteps = True
            printacs = True
        elif o in ("-h", "--help"):
            fmso_usage()
            sys.exit()
        elif o in ("-i", "--strictness"):
            cystrict = int(a)
        elif o in ("-s", "--steps"):
            printsteps = True
        elif o in ("-j", "--job"):
            myjob = int(a)
        elif o in ("-b", "--beststeps"):
            printbeststeps = True
        elif o in ("-n", "--normalize-to"):
            normalizeto = int(a)
        elif o in ("-x", "--scpcm"):
            doscpcmconv = True
        else:
            if buzzing : assert False, "The option " + o + " could not be recognized."
    try:
        from natsort import natsorted
        restargs = natsorted(restargs)
    except ImportError:
        print("Oh well, we cannot sort the files!")
    for allmyoutfile in restargs:
        try:
            allmyoutf = open(allmyoutfile,'r')
        except IOError:
            print("Cannot find such file!")
            sys.exit(10)
        allmyout = allmyoutf.read()
        allmyoutf.close()
        totjobs = allmyout.count('Entering Link 1')
        myroute = re.compile('#.*')
        myroutes = myroute.findall(allmyout)
        if len(restargs) > 1 : myjob = totjobs
        if totjobs > 1:
            while True:
                try:
                    if myjob == 0:
                        try:
                            myjob = int(raw_input('Which job out of '+str(totjobs)+' to search? '))
                        except NameError:
                            myjob = int(input('Which job out of '+str(totjobs)+' to search? '))
                    if myjob > 1:
                        patte = re.compile('Entering Link 1')
                        try:
                            for e in xrange(1,myjob+1): # 2nd argument is when to stop for this function -- i.e., myjob-th element is not considered
                                pasta1 = patte.search(allmyout).end() + 1
                                allmyout = allmyout[pasta1:]
                        except NameError:
                            for e in range(1,myjob+1): # 2nd argument is when to stop for this function -- i.e., myjob-th element is not considered
                                pasta1 = patte.search(allmyout).end() + 1
                                allmyout = allmyout[pasta1:]
                    if myjob < totjobs:
                        patte = re.compile('Normal termination')
                        pasta1 = patte.search(allmyout).end() + 1
                        allmyout = allmyout[:pasta1]
                    else:
                        if buzzing :
                            if myjob > totjobs: print("Not as many jobs present!")
                    myroute1 = myroutes[(myjob-1)]
                    break
                except KeyboardInterrupt:
                    if buzzing : print("Exit by user interference.")
                    sys.exit(1)
                except:
                    if buzzing : print("You entered something bad. Be ashamed and please try again.")
                    # print "Unexpected error:", sys.exc_info()[0]
        else:
            myjob = 1
            if len(myroutes) == 0:
                if buzzing : print('Not even a Route line has been reached! Exiting.')
                njobslist.append(0)
                njobslist1.append(0)
                exitstat = 5
                continue
            else:
                myroute1 = myroutes[0]
        
        #if buzzing : print('Separated...')
        
        nstepold = nstep
        if doscpcmconv:
            nstep = nstep + allmyout.count('self-consistent PCM reaction field, IExtIt=')
        else:
            nstep = nstep + allmyout.count('Step number')
        if nstep == nstepold:
            print()
            if 'NEF-NEF-NEF-NEF-NEF' in allmyout:
                if buzzing : print('This is a numeric-gradient optimization.')
                nstep = nstep + allmyout.count('GRADIENT ESTIMATION COMPLETE')
                import subprocess
                allmyout = subprocess.Popen(["sed", "-n", "/Current parameter values (internal coordinates)/,/PREDICTED CHANGE IN ENERGY /p;/PREDICTED CHANGE IN ENERGY\|O P T I M I Z A T I O N   P A R A M E T E R S/,/NUMERICAL EIGENVECTOR FOLLOWING MINIMUM SEARCH/p", restargs[0] ],stdout=subprocess.PIPE).communicate()[0]
            if nstep == nstepold and nstep == 0:
                print("For now, "+str(nstepold)+" steps have been done.")
                if ' Opt' in myroute1:
                    if buzzing : print('Not even a single step has been done! Exiting.')
                    njobslist.append(0)
                    njobslist1.append(0)
                    exitstat = 1
                    continue
                else:
                    if buzzing : print('This is NOT an optimization job! Route is:\n ' + myroute1[2:] + '\nExiting.')
                    njobslist.append(0)
                    njobslist1.append(0)
                    exitstat = 3
                    continue

        energycoef=0.6
        if doscpcmconv and 'SC-PCM: Erms=' in allmyout:
            energyline='SC-PCM: Erms='
            energyword=2
            if buzzing : print("This is an SC-PCM job.")
        elif 'ounterpoise' in allmyout:
            energyline='ounterpoise corrected'
            energyword=4
            if buzzing : print("This is a CP-based optimization.")
        elif 'SAC-CI' in allmyout:
            if ' #P ' in allmyout:
                energyline='TOTAL ENERGY  \=.*\n.*SAC-NV  coefficients'
            else:
                energyline='TOTAL ENERGY  \=.*\n.*SAC-NV  coefficients' # truly so at least for N
            energyword=3
            if buzzing : print("This is a SAC-CI-based optimization.")
        elif 'CCSD(T)=' in allmyout:
            energyline='CCSD\(T\)\='
            energyword=1
            if buzzing : print("This is a CCSD(T)-based optimization.")
        elif 'E(CORR)=' in allmyout:
            if ' #P ' in allmyout:
                energyline='E\(CORR\)\=.*\n.*NORM\(A\)\=.*\n.*CI/CC converged in.*\n.*Largest amplitude'
            else:
                energyline='E\(CORR\)\=.*\n.*NORM\(A\)\=.*\n.*Largest amplitude'
            energyword=3
            if buzzing : print("This is a CCSD-based optimization.")
        elif 'UMP4(SDTQ)=' in allmyout:
            energyline='UMP4\(SDTQ\)\='
            energyword=3
            if buzzing : print("This is an MP4(SDTQ)-based optimization.")
        elif 'UMP4(SDQ)=' in allmyout:
            energyline='UMP4\(SDQ\)\='
            energyword=3
            if buzzing : print("This is an MP4(SDQ)-based optimization.")
        elif 'UMP4(DQ)=' in allmyout:
            energyline='UMP4\(DQ\)\='
            energyword=3
            if buzzing : print("This is an MP2(DQ)-based optimization.")
        elif 'MP2' in allmyout:
            energyline='EUMP2'
            energyword=5
            if buzzing : print("This is an MP2-based optimization.")
        elif ' Total Energy, E(TD-HF/TD-KS)' in allmyout:
            energyline='Total Energy, E\(TD-HF\/TD-KS\)'
            energyword=4
            energycoef=200
            if buzzing : print("This is a TDHF/TDKS-based optimization.")
        else:
            energyline='SCF Don'
            energyword=4
            if buzzing : print("This is an SCF-based optimization.")

        convergencie = (0.00045, 0.0003, 0.0018, 0.0012)
        mfstringn = allmyout.find('RMS     Force        ')
        if mfstringn > -1 :
            mfstring = allmyout[mfstringn:mfstringn + 50].split()[3]
            if mfstring == '0.000010': # Opt=Tight
                convergencie = (0.000015, 0.000010, 0.000060, 0.000040)
            elif mfstring == '0.000001': # Opt=VeryTight
                convergencie = (0.000002, 0.000001, 0.000006, 0.000004)
            if normalizeto == 1:
                convergencie = (0.00045, 0.0003, 0.0018, 0.0012)
            elif normalizeto == 2:
                convergencie = (0.000015, 0.000010, 0.000060, 0.000040)
            elif normalizeto == 3:
                convergencie = (0.000002, 0.000001, 0.000006, 0.000004)

        if energyline=='SCF Don':
            qcscfc = allmyout.count('a.u. after')
            nqcscfc = allmyout.count('A.U. after')
            if qcscfc == 0 or qcscfc == nqcscfc:
                patte = re.compile(energyline + '.*\n.*NFock=')
                energias1 = patte.findall(allmyout)
            else:
                try:
                    import cStringIO as iioo
                except ImportError:
                    import io as iioo
                alloutagain = iioo.StringIO(allmyout+'\nGradGradGrad')
                ejkl = alloutagain.readline()
                curener = '' # in a loop, one cannot reference variables not defined out of loops
                while ejkl:
                    ejkl = alloutagain.readline()
                    if energyline in ejkl:
                        curener = ejkl
                    if 'GradGradGrad' in ejkl:
                        if len(curener) > 0:
                            if len(energias1) > 0:
                                if energias1[-1] != curener: energias1.append(curener)
                            else:
                                energias.append(curener)
                alloutagain.close()
            energias = [ float(i.split()[energyword].replace('D','E')) for i in energias ] + [ float(i.split()[energyword].replace('D','E')) for i in energias1 ]
#        elif energyline=='E\(CORR\)\=.*\n.*NORM\(A\)\=.*\n.*Largest amplitude':
#            patte = re.compile('.*'+energyline + '.*\n')
        else:
            patte = re.compile('.*'+energyline + '.*\n')
            energias1 = patte.findall(allmyout) # findall finds ONLY what is the regular expression provided, not the whole line -- hence the need for compile
            #if buzzing : sys.stdout.write(str(energias[0].split()[energyword-1]))
            if doscpcmconv:
                denergias = [ float(i.split()[4].replace('D','E')) for i in energias1 ]
            energias = [ float(i.split()[energyword].replace('D','E')) for i in energias1 ]
            
        if buzzing : sys.stdout.write('Found energies ('+str(len(energias))+')...')
        
        if not doscpcmconv:
            patte = re.compile('Maximum Force.*')
            maxforce1 = patte.findall(allmyout)
            maxforce = maxforce + [ normsteps(i.split()[2].replace('*','X'),convergencie[0],100500) for i in maxforce1 ]
            patte = re.compile('RMS     Force.*')
            rmsforce1 = patte.findall(allmyout)
            rmsforce = rmsforce + [ normsteps(i.split()[2].replace('*','X'),convergencie[1],100500) for i in rmsforce1 ]
            
            patte = re.compile('Maximum Displace.*')
            maxdispl1 = patte.findall(allmyout)
            maxdispl = maxdispl + [ normsteps(i.split()[2].replace('*','X'),convergencie[2],100500) for i in maxdispl1 ]
            patte = re.compile('RMS     Displace.*')
            rmsdispl1 = patte.findall(allmyout)
            rmsdispl = rmsdispl + [ normsteps(i.split()[2].replace('*','X'),convergencie[3],100500) for i in rmsdispl1 ]
            njobslist.append(len(rmsdispl)-sum(njobslist))
            njobslist1.append(len(energias)-sum(njobslist1))
            if buzzing : sys.stdout.write('Found conv. criteria ('+str(len(rmsdispl))+')....')
            ranalto2 = sum(convergencie)/4
        else:
            ranalto2 = 1
# end of multi-file reading

    
    if len(rmsdispl) == 0 and not doscpcmconv:
        if buzzing : print("No data for analysis. Exiting...")
        if exitstat == 0 : exitstat = 3
        sys.exit(exitstat)
    if len(rmsdispl) < len(energias)  and not doscpcmconv: # caviaro is used in xrange, which stops at 2nd arg before executing
        if len(restargs) > 1:
            energias.pop() # otherwise the input from multiple files will be quite messy
    caviaro = nstep
#        caviaro = (nstep-1)
 #   else:
  #      caviaro = nstep
    altogetherst=[]
    altogetherst2=[] 
    if doscpcmconv:
        altogetherst = denergias
        if len(altogetherst) < caviaro: caviaro = len(altogetherst)
    try:
        for muffin in xrange(0,caviaro):
          if not doscpcmconv:
#        if not is_number(maxforce[muffin]):
#            maxforce[muffin] = 100500
#        if not is_number(rmsforce[muffin]):
#            rmsforce[muffin] = 100500
#        if not is_number(maxdispl[muffin]):
#            maxdispl[muffin] = 100500
#        if not is_number(rmsdispl[muffin]):
#            rmsdispl[muffin] = 100500
#        altogetherst[muffin] = round(maxforce[muffin]/convergencie[0]+rmsforce[muffin]/convergencie[1]+maxdispl[muffin]/convergencie[2]+rmsdispl[muffin]/convergencie[3],5)
            try:
              altogetherst.append(round((maxforce[muffin]+rmsforce[muffin]+maxdispl[muffin]+rmsdispl[muffin])/4,5))
            except IndexError:
              caviaro = caviaro-1
          else:
            altogetherst2.append((energias[muffin]+denergias[muffin])/2)
    except NameError:
        for muffin in range(0,caviaro):
          if not doscpcmconv:
#        if not is_number(maxforce[muffin]):
#            maxforce[muffin] = 100500
#        if not is_number(rmsforce[muffin]):
#            rmsforce[muffin] = 100500
#        if not is_number(maxdispl[muffin]):
#            maxdispl[muffin] = 100500
#        if not is_number(rmsdispl[muffin]):
#            rmsdispl[muffin] = 100500
#        altogetherst[muffin] = round(maxforce[muffin]/convergencie[0]+rmsforce[muffin]/convergencie[1]+maxdispl[muffin]/convergencie[2]+rmsdispl[muffin]/convergencie[3],5)
            try:
              altogetherst.append(round((maxforce[muffin]+rmsforce[muffin]+maxdispl[muffin]+rmsdispl[muffin])/4,5))
            except IndexError:
              caviaro = caviaro-1
          else:
            altogetherst2.append((energias[muffin]+denergias[muffin])/2)
    minalto = min(altogetherst)
    maxalto = max(altogetherst)
    ranalto = maxalto - minalto
    if ranalto == 0:
        print('The optimization has only one step! I recommend using it...\nRecommended step is 1.')
        sys.exit(3)
    altogetherst = [ x/ranalto2 for x in altogetherst ]
    if buzzing : sys.stdout.write('Got their average...')
    minenergiasmin = min(energias)
    
    if not doscpcmconv:
        altogetherst2.append(altogetherst[0])
#        print('##Length of energias: '+str(len(energias)))
#        print('##Length of altogetherst: '+str(len(altogetherst)))
        try:
            for muffin in xrange(1,caviaro):
                altogetherst2.append(round(0.4*altogetherst[muffin] + energycoef*(energias[0] - energias[muffin])/minenergiasmin,5)) # 
        except NameError:
            for muffin in range(1,caviaro):
                altogetherst2.append(round(0.4*altogetherst[muffin] + energycoef*(energias[0] - energias[muffin])/minenergiasmin,5)) # 
        #altogetherst2.append(altogetherst2[caviaro-2])
    if buzzing : sys.stdout.write('Added energy to it...')
    
    if nstep < 3:
        print('Just 2 steps -- cannot calculate the moving average!')
        minaltogether3=[]; altogetherst3=altogetherst2
    else:
        altogetherst3=[] ; altogetherst3.append(altogetherst2[0]+altogetherst2[1]); altogetherst3.append(altogetherst2[0]+altogetherst2[1]+altogetherst2[2])
        try:
            for muffin in xrange(2,caviaro-1):
                altogetherst3.append(altogetherst2[muffin] + altogetherst2[muffin-2] + altogetherst2[muffin-1]) # 
        except NameError:
            for muffin in range(2,caviaro-1):
                altogetherst3.append(altogetherst2[muffin] + altogetherst2[muffin-2] + altogetherst2[muffin-1]) # 
        altogetherst3.append(altogetherst2[caviaro-1] + altogetherst2[caviaro-2])
        if buzzing : sys.stdout.write('Calculated 3-point moving average...')
    
    minenergia = getbestst(energias,nstep)
    if not doscpcmconv:
        minmaxforce = getbestst(maxforce,nstep)
        minrmsforce = getbestst(rmsforce,nstep)
        minmaxdispl = getbestst(maxdispl,nstep)
        minrmsdispl = getbestst(rmsdispl,nstep)
    minaltogether = getbestst(altogetherst,nstep)
    minaltogether2 = getbestst(altogetherst2,nstep)
    if nstep > 2 : minaltogether3 = getbestst(altogetherst3,nstep)
    if not doscpcmconv:
        selectedsteps = sorted(list(set(minenergia+minmaxforce+minrmsforce+minmaxdispl+minrmsdispl+minaltogether+minaltogether2+minaltogether3)))
    else:
        selectedsteps = sorted(list(set(minenergia+minaltogether+minaltogether2+minaltogether3)))
    if buzzing : sys.stdout.write('Sorted...\n\n')
    if printbeststeps :
        print('Best steps: '+' '.join([str(e) for e in selectedsteps])+' out of '+str(nstep)) # with [] it is list comprehension, without them, generator expression
        print('-----------------Best steps-------------------')
        print('By Energy: '+' '.join([str(e) for e in minenergia]))
        if not doscpcmconv:
            print('By Max Force: '+' '.join([str(e) for e in minmaxforce]))
            print('By RMS Force: '+' '.join([str(e) for e in minrmsforce]))
            print('By Max Displ: '+' '.join([str(e) for e in minmaxdispl]))
            print('By RMS Displ: '+' '.join([str(e) for e in minrmsdispl]))
        print('By Average of all: '+' '.join([str(e) for e in minaltogether]))
        print('By Average of all, incl. energy: '+' '.join([str(e) for e in minaltogether2]))
        if nstep > 2 : print('By Average of all + E, 3p moving average: '+' '.join([str(e) for e in minaltogether3]))

#        print len(maxforce), len(rmsdispl), len(altogetherst), len(altogetherst2), len(energias)
        #print('---------Convergence for best steps----------')
        #print('%-4s\t%6s\t%13s\t%13s\t%13s\t%13s\t%13s\t%13s\t%13s' % ('By','Energy','Max Force','RMS Force','Max Displ','RMS Displ','Average of all','Incl. energy','Mov. av.'))
        # the line above does not work, but I see no much need in it
    bestpyres=[]
    for rohr, danz in enumerate(selectedsteps):
        #debugfile=open(os.getcwd()+'rores','w') # this was the so-called virus from ziedins, ha ha
        #debugfile.write(str(rohr)+" "+str(danz)+'\n')
        #debugfile.close()
        bestpyres.append(danz)
        if buzzing :
          if not doscpcmconv:
            if printbeststeps : print('%-3d' % (danz)+':\t   ---\t'+'%8.2e' % (maxforce[danz-1])+'('+'%3s' % (maxforce[danz-1] < 1 and 'YES' or 'NO')+')\t' +'%8.2e' % (rmsforce[danz-1])+'('+'%3s' % (rmsforce[danz-1] < 1 and 'YES' or 'NO')+')\t' +'%8.2e' % (maxdispl[danz-1])+'('+'%3s' % (maxdispl[danz-1] < 1 and 'YES' or 'NO')+')\t' +'%8.2e' % (rmsdispl[danz-1])+'('+'%3s' % (rmsdispl[danz-1] < 1 and 'YES' or 'NO')+')\t' +'%8.2e' % (altogetherst[danz-1])+'('+'%3s' % (altogetherst[danz-1] < 1.0/ranalto and 'YES' or 'NO')+')\t' +'%8.2e' % (altogetherst2[danz-1])+'('+'%3s' % (altogetherst2[danz-1] < 1.0/ranalto and 'YES' or 'NO')+')\t' +'%8.2e' % (altogetherst3[danz-1])+'('+'%3s' % (altogetherst3[danz-1] < 1.0/ranalto and 'YES' or 'NO')+')')
          else:
            if printbeststeps : print('%-3d' % (danz)+':\t   ---\t'+'%8.2e' % (altogetherst[danz-1])+'('+'%3s' % (altogetherst[danz-1] < 1.0/ranalto and 'YES' or 'NO')+')\t' +'%8.2e' % (altogetherst2[danz-1])+'('+'%3s' % (altogetherst2[danz-1] < 1.0/ranalto and 'YES' or 'NO')+')\t' +'%8.2e' % (altogetherst3[danz-1])+'('+'%3s' % (altogetherst3[danz-1] < 1.0/ranalto and 'YES' or 'NO')+')')
    if buzzing : 
      if not doscpcmconv:
        printsteps and outputsteps(printacs,caviaro,energias,maxforce,rmsforce,maxdispl,rmsdispl,altogetherst,altogetherst2,altogetherst3)
      else:
        printsteps and outputscpcmsteps(printacs,caviaro,energias,altogetherst,altogetherst2,altogetherst3)
    if not doscpcmconv:
        cystarte = len(rmsdispl)
    else:
        cystarte = len(denergias)
    caviaro = len(altogetherst3)
    cyall = 100500
    while cystarte > 0 and cyall > 0: # python is weird for sequences: in slicing, second argument is first element NOT included
        if not doscpcmconv:
            maxforce = list(maxforce[0:cystarte])
            rmsforce = list(rmsforce[0:cystarte])
            maxdispl = list(maxdispl[0:cystarte])
            rmsdispl = list(rmsdispl[0:cystarte])
        altogetherst = list(altogetherst[0:cystarte])
        altogetherst2 = list(altogetherst2[0:cystarte])
# caviaro is number of steps to search in the current cycle
        altogetherst3 = list(altogetherst3[0:cystarte])
        #print("The whole array:")
        #print(zip(altogetherst3,xrange(0,len(altogetherst3))))
        #print("Sorted array:")
        #print(sorted(list(zip(altogetherst3,xrange(0,len(altogetherst3)))), key=lambda sorrow: sorrow[0]))
        #print("Which makes the best element:")
        #print(sorted(list(zip(altogetherst3,xrange(0,len(altogetherst3)))), key=lambda sorrow: sorrow[0])[0][1])
        try:
            if nstep > 16 : 
                altogetherst3 = list(altogetherst3[0:cystarte])
                caviaro = len(altogetherst3)
                bestaltogether = sorted(zip(altogetherst3,xrange(0,len(altogetherst3))), key=lambda sorrow: sorrow[0])[0][1]
            else :
                caviaro = len(altogetherst2)
                bestaltogether = sorted(zip(altogetherst2,xrange(0,len(altogetherst2))), key=lambda sorrow: sorrow[0])[0][1]
        except NameError:
            if nstep > 16 : 
                altogetherst3 = list(altogetherst3[0:cystarte])
                caviaro = len(altogetherst3)
                bestaltogether = sorted(list(zip(altogetherst3,range(0,len(altogetherst3)))), key=lambda sorrow: sorrow[0])[0][1]
            else :
                caviaro = len(altogetherst2)
                bestaltogether = sorted(list(zip(altogetherst2,range(0,len(altogetherst2)))), key=lambda sorrow: sorrow[0])[0][1]
        #print("But actually it is : "); print(bestaltogether)
        if buzzing : 
            print('\n\nWould recommend step '+str(bestaltogether+1)+' if no cycling is present.')
            print("Strictness for cycling search is "+str(cystrict))
# search gradually goes backwards with a step of "cyclist"; adsteps are the remaining steps (not being searched)
        if caviaro > 10:
            cyclist = int(max([round(caviaro/10),10,round(caviaro/4)]))
            adsteps = caviaro-cyclist
        else:
            cyclist = caviaro
            adsteps = 0
        #print("Caviaro is "+str(caviaro)+", cyclist is initially set to "+str(cyclist)+", adsteps is "+str(adsteps))
        if buzzing : print("Search for cycling starts at step "+str(caviaro-cyclist))
        if not doscpcmconv:
            cymfo=crudecycle([ float(roundstr % i) for i in maxforce[-1*cyclist:] ])
            cyrfo=crudecycle([ float(roundstr % i) for i in rmsforce[-1*cyclist:] ]) # round(i,cyctrict)
            cymdi=crudecycle([ float(roundstr % i) for i in maxdispl[-1*cyclist:] ])
            cyrdi=crudecycle([ float(roundstr % i) for i in rmsdispl[-1*cyclist:] ])
            cyall = cymfo+cyrfo+cymdi+cyrdi
        else:
            cyall = crudecycle([ float(roundstr % i) for i in denergias[-1*cyclist:] ])
# if any repeating values are found (to the certain precision) within last "cyclist" steps,
# cycling crude start is determined as the minimum for the four descriptors
        if cyall > 0:
    #        cystarte = min([x if x > 0 else 100500 for x in [cymfo,cyrfo,cymdi,cyrdi] ])+adsteps # sorry, no ternary until py 2.5
            cystarte = 100550+adsteps
            if not doscpcmconv:
              for x in [cymfo,cyrfo,cymdi,cyrdi]:
                if x > 0 and cystarte > x+adsteps: cystarte = x+adsteps
            else:
              if cystarte > cyall+adsteps: cystarte = cyall+adsteps
            if buzzing : print('Cycling is highly probable after step '+str(cystarte)+'!!!')
            if caviaro > 10:
                cyclist_one = cyclist
                #print("cyclist_one:"+str(cyclist_one))
# currently there are "cyclist_one" steps of cycling detected
                if not doscpcmconv:
                    thoromf = thoroughcycle([ float(roundstr % i) for i in maxforce[-1*cyclist:] ])
                    thoroaf = thoroughcycle([ float(roundstr % i) for i in rmsforce[-1*cyclist:] ])
                    thoromd = thoroughcycle([ float(roundstr % i) for i in maxdispl[-1*cyclist:] ])
                    thoroad = thoroughcycle([ float(roundstr % i) for i in rmsdispl[-1*cyclist:] ])
                else:
                    thoromf = thoroughcycle([ float(roundstr % i) for i in denergias[-1*cyclist:] ])
                while cyclist < caviaro:
                    #print("cyclist:"+str(cyclist))
# now we are stepping back by the step of "cyclist_one"; if more cycling steps are found, 
# we further lower the starting step (by "cyclist_one") and repeat. "cycling" is the current
# lowest step, and we are checking its next possible value
                    if not doscpcmconv:
                        thoromf_one = thoroughcycle([ float(roundstr % i) for i in maxforce[-1*(cyclist+cyclist_one):] ])
                        thoroaf_one = thoroughcycle([ float(roundstr % i) for i in rmsforce[-1*(cyclist+cyclist_one):] ])
                        thoromd_one = thoroughcycle([ float(roundstr % i) for i in maxdispl[-1*(cyclist+cyclist_one):] ])
                        thoroad_one = thoroughcycle([ float(roundstr % i) for i in rmsdispl[-1*(cyclist+cyclist_one):] ])
                        if thoromf_one > thoromf or thoroaf_one > thoroaf or thoromd_one > thoromd or thoroad_one > thoroad:
                            thoromf = thoromf_one
                            thoroaf = thoroaf_one
                            thoromd = thoromd_one
                            thoroad = thoroad_one
                        else:
                            #print("No more cycles found (step "+str(caviaro-cyclist)+")")
                            break
                    else:
                        thoromf_one = thoroughcycle([ float(roundstr % i) for i in denergias[-1*(cyclist+cyclist_one):] ])
                        if thoromf_one > thoromf:
                            thoromf = thoromf_one
                        else:
                            break
                    cyclist += cyclist_one
                    #print("Now cycles found is: "+str(max([thoromf,thoroaf,thoromd,thoroad])))
    
# now we are iterating within the "cyclist_one" number of steps, increasing the starting step number while the number
# of cycling steps stays the same
                cyfiste = 1
                cystarte = cyclist
                while cyfiste < cyclist_one:
                    #print("cystarte:"+str(cystarte))
                    if not doscpcmconv:
                        thoromf_one = thoroughcycle([ float(roundstr % i) for i in maxforce[-1*(cyclist-cyfiste):] ])
                        thoroaf_one = thoroughcycle([ float(roundstr % i) for i in rmsforce[-1*(cyclist-cyfiste):] ])
                        thoromd_one = thoroughcycle([ float(roundstr % i) for i in maxdispl[-1*(cyclist-cyfiste):] ])
                        thoroad_one = thoroughcycle([ float(roundstr % i) for i in rmsdispl[-1*(cyclist-cyfiste):] ])
                        #print("And now cycles found is: "+str(max([thoromf_one,thoroaf_one,thoromd_one,thoroad_one])))
                        if thoromf_one == thoromf and thoroaf_one == thoroaf and thoromd_one == thoromd and thoroad_one == thoroad:
                            cystarte -= 1
                        else:
                            break
                    else:
                        thoromf_one = thoroughcycle([ float(roundstr % i) for i in denergias[-1*(cyclist-cyfiste):] ])
                        if thoromf_one == thoromf:
                            cystarte -= 1
                        else:
                            break
                    cyfiste += 1
                cystarte = len(altogetherst3) - cystarte - 1
            print("Cycling probably starts at step "+str(cystarte)+".")
        else:
            if buzzing : print('No cycling is detected. Congratulations!')

        allthebest = sum(njobslist)
        jctms="Jobs contain this many steps: "
        for u in [ str(i)+' ' for i in njobslist ]:
            jctms=jctms+u
        print(jctms)
        bestjobbb = len(njobslist)
        while bestaltogether < allthebest: # bestaltogether+1 <= allthebest, i.e., within the array
            bestjobbb = len(njobslist)
            #print("Best job is "+str(bestaltogether)+" , sum of jobs: "+str(allthebest)+" , number  of files less than actual one: "+str(bestjobbb))
            #print(njobslist)
            njobslist.pop()
            njobslist1.pop()
            allthebest = sum(njobslist)
#        njobslist1.pop(); njobslist.pop() # pop() returns the removed element, so this must go in a separate line
        allthebest1 = sum(njobslist1) - allthebest # we need to get the difference for all the steps before the actual job
        #print("Starpiba ir "+str(allthebest1))
        #print("Atnemts tiek "+str(allthebest))

        bestofthebest = bestaltogether - allthebest + 1 + allthebest1
        print('\n\nRecommended step is '+ str(bestaltogether+1) + ' (or '+str(bestofthebest)+' within job # '+str(bestjobbb) + ' )')
    print("ATTENTION! The files came in the following order:")
    for i in restargs:
        print(i)
    print("You may want to sort them differently if the order above is not what You wanted.")
    
if __name__ == "__main__":
    main()


