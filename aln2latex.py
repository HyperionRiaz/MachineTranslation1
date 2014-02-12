#!/usr/bin/env python

# visualize IBM one-to-many alignments in a LaTeX document
# (c) 2008-2014 Ulrich Germann
import sys,os,re
from optparse import OptionParser,Option,OptionValueError

class MultiOpt(Option):
    """
    Define an option class that allows multiple specifications 
    for the option parser. 
    """
    ACTIONS       = Option.ACTIONS + ("extend",)
    STORE_ACTIONS = Option.STORE_ACTIONS + ("extend",)
    TYPED_ACTIONS = Option.TYPED_ACTIONS + ("extend",)
    ALWAYS_TYPED_ACTIONS = Option.ALWAYS_TYPED_ACTIONS + ("extend",)
    
    def take_action(self, action, dest, opt, value, values, parser):
        if action == "extend":
            values.ensure_value(dest, []).append((value,opt))
        else:
            Option.take_action(self, action, dest, opt, value, values, parser)

# auxiliary functions for producing latex code
def colheader(w):
    # return r'\multicolumn{1}{@{}c@{}}{\makebox[%s][c]{\rput[lB]{50}{%s}}}'\
    return r'\multicolumn{1}{@{}c@{}}{\makebox[%s][l]{\rotatebox[origin=lb]{50}{%s}}}'\
        %("2.7ex",w)

def amatrix(s,t,a):
    T = [[0 for x in t] for y in s]
    for i in xrange(len(a)):
        for k in xrange(len(a[i][0])):
            if a[i][0][k] == 0: continue
            if a[i][1] == "-f":
                T[a[i][0][k]-1][k] += i + 1
            else:
                T[k][a[i][0][k]-1] += i + 1
                pass
            pass
        pass
    return T
    
def blob(colors,val):
    if not val: return ''
    return r'\raisebox{-1ex}{%s\rule{2.8ex}{2.8ex}}'%(colors[val])


def texscape(w):
    w = w.replace("%","\%")
    w = w.replace("{","$\{$")
    w = w.replace("{","$\}$")
    return w

colors = ('','')
def show(i,s,t,a):
    A = amatrix(s,t,a)
    print r'\begin{tabular}{r*{%d}{|@{}c@{}}|}'%len(t)
    print colheader('')
    for w in t: print "&%s"%colheader(texscape(w))
    print r'\\\cline{2-%d}'%(len(t)+1)
    M = [[blob(colors,A[r][c])
          for c in xrange(len(t))] 
          for r in xrange(len(s))]
    for r in xrange(len(s)):
        print texscape(s[r]),'&', '&'.join(M[r]),r'\\\cline{2-%d}'%(len(t)+1)
        pass
    print r'\end{tabular}\\\vspace{3em}'
    print 
    
            
if __name__ == "__main__":

    parser = OptionParser(option_class=MultiOpt, usage="%prog [options]")
    parser.add_option("-s",dest="src",help="source text file (mandatory)",nargs=1)
    parser.add_option("-t",dest="trg",help="target text file (mandatory)",nargs=1)
    parser.add_option("-f",dest="aln",action="extend",
                      help="forward alignment file (maps target to source)")
    parser.add_option("-i",dest="aln",action="extend",
                      help="inverse alignment file (maps source to target)")
    parser.add_option("-r",dest="range",
                      help="range(s) of sentences to process, e.g. 1,3,4,6-9")
    parser.add_option("-d",dest="diff",action="store_true",
                      help="diff mode: only show alignments where both differ")
    o,a = parser.parse_args(sys.argv)

    assert o.aln, "at least one alignment must be given"
    assert len(o.aln) <= 2, "at most two alignments may be given"

    # load source, target, alignments
    src  = [x.strip().split() for x in open(o.src)]
    trg  = [x.strip().split() for x in open(o.trg)]
    aln  = [[[int(y) for y in x.strip().split()]
             for x in open(z[0])] for z in o.aln]
    if len(aln) > 1: 
        colors = ('',r'\color{blue}',r'\color{red}','')
        pass
    
    # for snt in src:
    #     for w in snt: 
    #         if not re.match(r'^[a-zA-Z,;:?]+$',w):
    #             print w
    #             pass
    #         pass
    #     pass

    # sys.exit(0)
    

    # determine the selection of sentences to include
    sel = o.range
    if not sel: sel = "%d-%d"%(0,len(src))

    print r'\documentclass{article}'
    # print r'\usepackage[pdf]{pstricks}'
    # print r'\usepackage{auto-pst-pdf}'
    # print r'\usepackage{pst-node}'
    print r'\usepackage{graphicx}'
    print r'\usepackage{xcolor}'
    print r'\usepackage[utf8x]{inputenc}'
    print r'\usepackage[german]{babel}'
    print r'\begin{document}\sffamily\small'
    print r'\thispagestyle{empty}\pagestyle{empty}'
    print r'\renewcommand{\arraystretch}{.9}'
    print r'\setlength{\parindent}{0pt}'
    if len(aln) > 1:
        print r"{%s\rule{2.8ex}{2.8ex}}: %s\\"%(colors[1],o.aln[0])
        print r"{%s\rule{2.8ex}{2.8ex}}: %s\\"%(colors[2],o.aln[1])
        pass
    for s in sel.split(","):
        r = [int(x) for x in s.split("-")]
        assert len(r) < 3, "Error in range specification"
        if (len(r) == 1): r = [r]
        else:             r = xrange(r[0],r[1])
        for i in r:
            if o.diff and (len(o.aln) != 2 or aln[0][i] == aln[1][i]):
                continue
            a = [[aln[k][i],o.aln[k][1]] for k in xrange(len(o.aln))]
            show(i,src[i],trg[i],a)
        pass
    print r'\end{document}'
    pass
