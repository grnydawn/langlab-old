# -*- coding: utf-8 -*-

import re
import os
import subprocess

try:
    import configparser
except:
    import ConfigParser as configparser

from langlab.util import which

STR_EX = b'execve('
STR_EN = b'ENOENT'
STR_UF = b'<unfinished'
STR_RE = b'resumed>'

# command is a list
def run_command(command, cwd):
    p = subprocess.Popen(" ".join(command),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, shell=True, cwd=cwd)
    return iter(p.stdout.readline, b'')

class GenericCompiler(object):
    compid = None
    compnames = []
    openmp = None
    file_exts = None
    fpp = ''

    discard_opts_noarg = [ ]
    discard_opts_arg = [ ]

    def get_discard_opts_noarg(self):
        return [ '-c' ]

    def get_discard_opts_arg(self):
        return [ '-o', '-l', '-L', '-W' ]

    def _getmacro(self, macro):
        splitmacro = macro.split('=')
        if len(splitmacro)==1:
           return (splitmacro[0], None)
        elif len(splitmacro)==2:
            return tuple(splitmacro)
        else:
            raise

    def parse_option(self, options, pwd):
        incs = []
        macros = []
        openmp = []
        srcs = []
        flags = []

        discard_flag = False

        iflag = False
        dflag = False

        for item in options[1:]:

            if discard_flag:
                discard_flag = False
                continue

            if iflag:
                for p in item.split(':'):
                    if p[0]=='/':
                        incs.append(p)
                    else:
                        incs.append(os.path.realpath('%s/%s'%(pwd,p)))
                iflag = False
                continue
            if dflag:
                macros.append(self._getmacro(item))
                dflag = False
                continue

            if item.startswith('-I'):
                if len(item)>2:
                    for p in item[2:].split(':'):
                        if p[0]=='/':
                            incs.append(p)
                        else:
                            incs.append(os.path.realpath('%s/%s'%(pwd,p)))
                else: iflag = True
            elif item.startswith('-D'):
                if len(item)>2:
                    macros.append(self._getmacro(item[2:]))
                else: dflag = True
            elif self.openmp_opt and any(not re.match(r'%s\Z'%pattern, item) is None for pattern in self.openmp_opt):
                    openmp.append(item)
            elif item.startswith('-'):
                if item in self.get_discard_opts_noarg():
                    pass
                elif any( item.startswith(f) for f in self.get_discard_opts_arg() ):
                    for f in self.get_discard_opts_arg():
                        if item==f:
                            if len(item)==len(f):
                                discard_flag = True
                            break
                else:
                    flags.append(item)
            elif self.file_exts and item.split('.')[-1] in self.file_exts:
                if item[0]=='/':
                    srcs.append(item)
                else:
                    srcs.append(os.path.realpath('%s/%s'%(pwd,item)))
            else:
                flags.append(item)

        if len(srcs)>0:
            return (srcs, incs, macros, openmp, flags)
        else:
            return ([], [], [], [], [])

def createCompiler(compid, compilers):
    for comp in compilers:
        if comp.compnames and compid in comp.compnames:
            return comp()


def _getpwd(env):
    for item in env:
        if item.startswith('PWD='):
            return item[4:]
    return None

def compflag(command, compilers, workdir=None, includes=None, macros=None, imports=None):

    cfg = configparser.RawConfigParser()
    cfg.optionxform = str

    if includes:
        cfg.add_section('include')
        for inc in includes:
            for i in inc.split(':'):
                cfg.set('include', i, '')

    if macros:
        cfg.add_section('macro')
        for key, value in macros.items():
            cfg.set('macro', key, value)

    if imports:
        cfg.add_section('import')
        for key, value in imports.items():
            cfg.set('import', key, value)

    shell = which("sh")
    strace = which("strace")

    if not os.path.isfile(strace):
        raise Exception("'strace' is not found.")

    # TODO: check if strace works properly

    argv = [
        strace,
        "-f", "-q", "-s", "100000", "-e", "trace=execve", "-v",
        "--", shell, "-c", "'%s'" % command
    ]

    flags = {}

    for line in run_command(argv, workdir):
        pos_execve = line.find(STR_EX)
        if pos_execve >= 0:
            pos_enoent = line.rfind(STR_EN)
            if pos_enoent < 0:
                pos_last = line.rfind(STR_UF)
                if pos_last < 0:
                    pos_last = line.rfind(b']')
                else:
                    pos_last -= 1
                if pos_last >= 0:
                    try:
                        lenv = {} 
                        parsestr = b"exepath, cmdlist, env = " + line[pos_execve+len(STR_EX):(pos_last+1)]
                        exec(parsestr, None, lenv)
                        exepath = lenv["exepath"]
                        cmdlist = lenv["cmdlist"]
                        env = lenv["env"]
                        compid = cmdlist[0].split('/')[-1]
                        if exepath and cmdlist and compid==cmdlist[0].split('/')[-1]:
                            compiler = createCompiler(compid, compilers)
                            if compiler:
                                srcs, incs, macros, openmp, options = compiler.parse_option(cmdlist, _getpwd(env))
                                if len(srcs)>0:
                                    for src in srcs:
                                        if src in flags:
                                            flags[src].append((exepath, incs, macros, openmp, options))
                                        else:
                                            flags[src] = [ (exepath, incs, macros, openmp, options) ]
                    except Exception as err:
                        raise

    for fname, incitems in flags.items():
        if len(incitems)>0:
            # save the last compiler set
            compiler = incitems[-1][0]
            incs = incitems[-1][1]
            macros = incitems[-1][2]
            options = incitems[-1][4]

            if cfg.has_section(fname):
                print('Warning: %s section is dupulicated.' % fname)
            else:
                cfg.add_section(fname)
                cfg.set(fname,'compiler', compiler)
                cfg.set(fname,'compiler_options', ' '.join(options))
                cfg.set(fname,'include',':'.join(incs))
                for name, value in macros:
                    cfg.set(fname, name, value)

    return cfg
