#!/usr/bin/env python
# -*- coding: sjis -*-

import os, sys, fnmatch
import os.path
from shutil import ignore_patterns
from shutil import copystat
import errno
import re

class Error(EnvironmentError):
    pass

kifuRegEx = re.compile(r'[+-][0-9]{2}[1-9]{2}(FU|KY|KE|GI|KI|KA|HI|OU|TO|NY|NK|NG|UM|RY)')

def copytree2(src, dst, symlinks=False, ignore=None, pat=None):
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    if pat is not None:
        pat_names = pat(src, names)
    else:
        pat_names = set()

    os.makedirs(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue

        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree2(srcname, dstname, symlinks, ignore, pat)
            else:
                #copy2(srcname, dstname)
                annotateFile(srcname, dstname)

            # XXX What about devices, sockets etc.?
        except (IOError, os.error), why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error, err:
            errors.extend(err.args[0])
    try:
        copystat(src, dst)
    except WindowsError:
        # can't copy file access times on Windows
        pass
    except OSError, why:
        errors.extend((src, dst, str(why)))
    if errors:
        raise Error(errors)

KOMASTR = {'FU':"��",'KY':"��",'KE':"�j",'GI':"��",'KI':"��",'KA':"�p",'HI':"��",'OU':"��",'TO':"��",'NY':"����",'NK':"���j",'NG':"����",'UM':"�n",'RY':"��"}

dou = 'AA'

SUJISTR  = ['0',"�P","�Q","�R","�S","�T","�U","�V","�W","�X"]

DANSTR = ['��',"��","��","�O","�l","��","�Z","��","��","��"]

def sujidan(str):
    global dou
    koma = KOMASTR.get(str[4:],r'�H')
    if str[0:2] == '00':
        return SUJISTR[int(str[2])] + DANSTR[int(str[3])] + koma + r'��'
    else:
        if str[2:4] == dou:
            return r'��'+koma + "("+str[0:2]+")"
        else:
            dou = str[2:4]
            return SUJISTR[int(str[2])] + DANSTR[int(str[3])] + koma + "("+str[0:2]+")"

def kifuMatch(match):
    str = r''
    kifu = match.group()
    if kifu[0] == '+':
        str += r'��'
    elif kifu[0] == '-':
        str += r'��'
    return str + sujidan(kifu[1:])

def convertIt(str):
    dou = 'AA'
    ma = kifuRegEx.sub(kifuMatch,str)
    return ma

def annotateFile(src,dst):
    print "processing... " + src
    srcfile = open(src, 'r')
    dstfile = open(dst, 'w')
    for line in srcfile:
        if line.startswith(r"'**"):
            #print line
            dstfile.write(convertIt(line))
        else:
            dstfile.write(line)
    srcfile.close()
    dstfile.close()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "%s src dst" % sys.argv[0]
        print
        print "copy src dir's CSA file to dst dir with annotate."
    else:
        copytree2(sys.argv[1], sys.argv[2], ignore=ignore_patterns("*.kif",".DS_Store"))
