import sys

# (C) 2017 by Alvaro Alea Fernandez (alvaroalea AT gmail.com)
# Under GPL2 License
# https://github.com/alvaroalea/hpgl2gcode
#
# Based on work of: gogela  https://github.com/gogela/hpgl2gcode
#
# Modified to work with the gcode of inkscape plugin inkcut 1.0
# http://inkcut.sourceforge.net/


# This class provides the functionality we want. You only need to look at
# this if you want to know how this works. It only needs to be defined
# once, no need to muck around with its internals.
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration
    
    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False


#open file passed as argument
if len(sys.argv)>1:
 f = open(sys.argv[1],'r')
else:
 print('usage: python3 hpgl2code.py inputfile.hpgl > outputfile.gcode')
 sys.exit(1)

#decoded commands
#PA x,y;  //pen advance xy unit=25um ie 40 units/mm (partial, dont allow several coordenates)
#PU x,y;    //pen up - replace with G1 Z'up' (safe Z heigh constant) plus pen advance
#PD x,y;    //pen down - - replace with G1 Z'dn' (engrawing depth constant) plus pen advance

#no decoded (ignored)
#IN  initial state
#SP1 select pen 1

#constants
zup=5 # 5mm should be safe enough
zdn=0 # using 0, for engraving negative values to be used
upm=40 # hpgl units per mm (in theory should be 40.2)
epm=0 # extrude per mm - in case I'm trying to plot with PLA
feed=500 #default feedrate

#init stuff - whatever g commands 
print("; Standar Header")
print("G21") # units in mm
print("G90") # units are absolute
print("G92 X0 Y0 Z0") # set the current position as home, border of vynil with desired depth in cut.
print("G1 Z",zup," F",feed,sep="") # pen up before 1st move
print("; START to cut")

#process the input file
xlast=0
ylast=0
fcon = f.read()
cmdlist = fcon.split(";")
for line in cmdlist: # f:
 co=line[:2]
 pa=line[2:]
# print("DEBUG1>",line," CO>",co," PA>",pa,"[EOF]")
 if pa.find(',')!=-1:
   palist=pa.split(",")
#   print("DEBUG2>",palist)
   x=int(palist[0])/upm
   y=int(palist[1])/upm
 else:
   x=xlast
   y=ylast

 for case in switch(co):
    if case('PA'):
        print("G1 X",x," Y",y," F",feed,sep="")
        break
    if case('PD'):
        print("G1 Z",zdn," F",feed,sep="")
        print("G1 X",x," Y",y," F",feed,sep="")
        break
    if case('PU'):
        print("G1 Z",zup," F",feed,sep="")
        print("G1 X",x," Y",y," F",feed,sep="")
        break
    xlast=x
    ylast=y


print("; END of cutting")
print("G1 Z25")
print("G1 X0 Y0") # move to a safe place
print("M84") # motors off
