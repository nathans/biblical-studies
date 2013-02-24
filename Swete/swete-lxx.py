#! /usr/bin/env python
# Swete-LXX: Download png images of Swete's LXX from CCEL
#
# Copyright 2009, 2011 Nathan Smith <nathan@smithfam.info>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os, urllib

def swetegrab(vol,page,offset):
    if os.path.exists("Vol%d/%04d.png" % (vol,page)):
        print "Already have %d:%04d" % (vol,page)
        return
    url = urllib.urlopen("http://www.ccel.org/ccel/swete/lxx%d/png/%04d=%d.png" % (vol,(offset+page),page))
    print "http://www.ccel.org/ccel/swete/lxx%d/png/%04d=%d.png - > Vol%d/%04d.png" % (vol,(offset+page),page,vol,page)
    file = open("Vol%d/%04d.png" % (vol,page),"w")
    image = url.read()
    file.write(image)
    url.close()
    file.close()

# [Range, offset]
# Add one to the page count to generate the ranges
volone = [range(1,831), 28]
voltwo = [range(1,881), 16]
volthree = [range(1,905), 24]

volumes = [volone, voltwo, volthree]

for x in range(len(volumes)):
    if not os.path.exists("Vol%d" % (x+1)):
        os.mkdir("Vol%d" % (x+1))
    for page in volumes[x][0]:
        swetegrab(x+1,page,volumes[x][1])
