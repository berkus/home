# -*- coding: utf-8 -*-

from SCons.Script import *
from os.path import join, dirname, abspath, isdir
from thirdparty import UseThirdParty
from subprocess import call, Popen, PIPE
import atexit
supported_platforms = ['win32', 'posix', 'darwin']
valid_modes = [
    'debug',
    'release',
    'bullseye',
    'purify',
    'valgrind',
    'quantify',
    ]
globalEnv = DefaultEnvironment()
Alias('neat')
if globalEnv['PLATFORM'] == 'win32':
    Clean('neat', Glob('*.pdb'))


def GetVariantDir(name):
    mode = ARGUMENTS.get('mode', 'debug')
    if mode not in valid_modes:
        raise NameError('invalid mode', mode)
    if globalEnv['PLATFORM'] not in supported_platforms:
        raise NotImplementedError('unsupported platform', globalEnv['PLATFORM'])
    return join(name, 'build', globalEnv['PLATFORM'] + '-' + mode)


def withExtension(node, ext):
    return '{name}.{extension}'.format(name=str(node[0]).split('.')[0], extension=ext)


def binPath(libpath):
    lib = abspath(libpath).split(os.sep)
    bin = lib[0] + os.sep
    lib = lib[1:len(lib) - 1]
    for comp in lib:
        bin = join(bin, comp)
    bin = join(bin, 'bin')
    return bin


class BuildEnvironment:

    env = None
    project = 'project'
    version = '1.0'
    mode = 'debug'

    def __init__(self, project, version='install'):
        self.env = Environment().Clone()
        self.project = project
        self.version = version
        self.mode = ARGUMENTS.get('mode', 'debug')
        if self.mode not in valid_modes:
            raise NameError('invalid mode', self.mode)
        if self.env['PLATFORM'] not in supported_platforms:
            raise NotImplementedError('unsupported platform', self.env['PLATFORM'])
        self.env['MODE'] = self.mode
        self.env['VARIANT'] = '$PLATFORM-$MODE'
        self.env['REPOSITORY'] = os.environ['REPOSITORY']
        if self.env['PLATFORM'] == 'win32':
            self.env['VARIANT'] = '$PLATFORM-$MODE'
            self.__loadWindowsEnvironment()
        else:
            self.env['VARIANT'] = '$PLATFORM'
            if self.env['PLATFORM'] == 'darwin':
                self.__loadDarwinEnvironment()
            else:
                self.__loadPosixEnvironment()
        self.__setupBuilders()
        self.__setupProjectPaths()
        if ARGUMENTS.get('mode', 'debug') == 'bullseye':
            self.__setupBullsEye()
        if ARGUMENTS.get('mode', 'debug') == 'gcov':
            self.__setupGCov()

    def __loadWindowsEnvironment(self):
        self.env.Append(CXXFLAGS=['/EHsc', '/W3', '/WX'])
        self.env.Append(CPPDEFINES=[('_WIN32_WINNT', '0x0501')])
        self.env['DEBUGSUFFIX'] = ''
        if self.env['MODE'] != 'release':
            self.env.Append(CXXFLAGS=['/Zi'])
            self.env.Append(LINKFLAGS=['/DEBUG'])
            self.env['DEBUGSUFFIX'] = 'd'
        self.env.Append(CXXFLAGS=['/MD$DEBUGSUFFIX'])

    def __loadPosixEnvironment(self):
        self.env.Append(CXXFLAGS=['-Wall', '-Werror'])
        if self.env['MODE'] != 'release':
            self.env.Append(CXXFLAGS=['-g'])

    def __loadDarwinEnvironment(self):
        self.env.Append(CXXFLAGS=['-Wall'])
        if self.env['MODE'] != 'release':
            self.env.Append(CXXFLAGS=['-g'])

    def __setupBuilders(self):
        protob = Builder(action=protobuf_builder, emitter=protobuf_emitter)
        self.env['BUILDERS']['ProtoBuf'] = protob

    def __setupProjectPaths(self):
        this = join('#', self.project)
        self.env['PROJECT'] = self.project
        self.env['PROJECTDIR'] = this
        self.env['INSTALLDIR'] = join(this, self.version, '$VARIANT')
        self.env['BUILDDIR'] = join(this, 'build', '$VARIANT')
        self.env['BINDIR'] = join('$INSTALLDIR', 'bin')
        self.env['LIBDIR'] = join('$INSTALLDIR', 'lib')
        self.env['INCLUDEDIR'] = join('$INSTALLDIR', join('include', self.project))
        self.env['TESTSDIR'] = join('$INSTALLDIR', 'tests')
        self.env.Append(CPPPATH=['main/include'])
        self.env.Append(LIBPATH=[])
        self.env.Append(LIBS=[])
        self.env.Clean(self.project, join(this, 'install', '$VARIANT'))
        self.env.Clean(self.project, join(this, 'build', '$VARIANT'))
        self.env.Alias('neat')
        self.env.Clean('neat', join(this, 'build'))
        self.env.Clean('neat', join(this, 'install'))

    def __setupBullsEye(self):
        proj_dir = self.env.GetBuildPath('$PROJECTDIR')
        self.env['COVFILE'] = join(proj_dir, self.project + '.cov')
        self.env['ENV']['HOME'] = proj_dir
        self.env['ENV']['COVFILE'] = self.env['COVFILE']
        self.env.Clean(self.project, self.env['COVFILE'])
        call('cov01 --no-banner -1')

    def __setupGCov(self):
        self.env.Append(CXXFLAGS=['-fprofile-arcs', '-ftest-coverage'])
        self.env.Append(LIBS=['gcov'])

    def StaticLibrary(
        self,
        name=None,
        exclude=None,
        extras=None,
        ):

        if not name:
            name = self.project
        if extras:
            self.env.MergeFlags(extras)
        sources = Glob('main/src/*.cc')
        if exclude:
            sources = list(set(sources) - set(Glob(exclude)))
        lib = self.env.StaticLibrary(name, sources)
        self.env.Install('$LIBDIR', lib)
        self.env.Install('$INCLUDEDIR', Glob('main/include/*.h'))
        return lib

    def ProtocolBuffers(self, name=None):
        if not name:
            name = '{0}_protobuf'.format(self.project)
        protofiles = Glob('main/proto/*.proto')
        if len(protofiles) > 0:
            self.env.Append(CPPPATH=[join(self.project, 'main/proto')])
            self.UseThirdParty('PROTOBUF')
            sources = self.env.ProtoBuf(protofiles)
            if self.OnWindows():
                lib = self.env.StaticLibrary(name, sources[0], CPPPATH=['$CPPPATH', '.'])
            else:
                lib = self.env.StaticLibrary(name, sources[0], CPPPATH=['$CPPPATH', '.'],
                                             CPPFLAGS=['$CPPFLAGS', '-fPIC'])
            self.env.Install('$INCLUDEDIR', sources[1])
            self.env.Install('$LIBDIR', lib)
            return lib

    def DynamicLibrary(self, name=None, extras=None):
        if not name:
            name = self.project
        if extras:
            self.env.MergeFlags(extras)
        if self.OnWindows():
            result = self.__buildWindowsDLL(name)
        else:
            result = self.__buildPosixSO(name)
        self.env.Install('$INCLUDEDIR', Glob('main/include/*.h'))
        return result

    def __buildWindowsDLL(self, name):
        sources = Glob('main/src/*.cc')
        rcfile = 'main/src/' + name + '.rc'
        if os.path.exists(rcfile):
            sources.append(self.env.RES(rcfile))
        dll = self.env.SharedLibrary(name, sources, CPPDEFINES=['$CPPDEFINES', 'BUILDING_DLL'])
        so = self.env.Install('$BINDIR', dll[0])
        lib = self.env.Install('$LIBDIR', dll[1])
        self.env.Depends(lib, so)
        if self.mode != 'release':
            self.env.Install('$BINDIR', withExtension(dll, 'pdb'))
        return lib

    def __buildPosixSO(self, name):
        so = self.env.SharedLibrary(name, Glob('main/src/*.cc'))
        so = self.env.Install('$BINDIR', so)
        return so

    def Executable(self, name=None, extras=None):
        if not name:
            name = self.project
        if extras:
            self.env.MergeFlags(extras)
        sources = Glob('main/src/*.cc')
        if self.env['PLATFORM'] == 'win32':
            rcfile = 'main/src/' + name + '.rc'
            if os.path.exists(rcfile):
                sources.append(self.env.RES(rcfile))
        exe = self.env.Program(name, sources)
        self.env.Install('$BINDIR', exe)
        if self.env['PLATFORM'] == 'win32':
            if self.mode != 'release':
                self.env.Install('$BINDIR', withExtension(exe, 'pdb'))
        return exe

    def OnWindows(self):
        return self.env['PLATFORM'] == 'win32'

    def UnitTests(self, extras=None):
        testEnv = self.env.Clone()
        testEnv.MergeFlags(extras)
        UseThirdParty(testEnv, 'GTEST')
        UseThirdParty(testEnv, 'BOOST')
        shared = Glob('test/src/shared.cc')
        for t in Glob('test/src/*_test.cc'):
            test = testEnv.Program([t, shared])
            unit = testEnv.Install('$TESTSDIR', test)
            if self.env['PLATFORM'] == 'win32':
                testEnv.Append(LINKFLAGS=['/SUBSYSTEM:CONSOLE'])
                if self.mode != 'release':
                    testEnv.Install('$TESTSDIR', withExtension(test, 'pdb'))
            if self.env['PLATFORM'] == 'posix':
                testEnv.Append(LIBS=['pthread'])
            if ARGUMENTS.get('tests', 'yes') == 'yes':
                testEnv.AddPostAction(unit, UnitTestAction)

    def UpdateEnvironment(self, flags):
        self.env.MergeFlags(flags)

    def UseThirdParty(self, name, libs=[]):
        UseThirdParty(self.env, name, libs)

    def UseProjectLibrary(self, name):
        project = join('#', name)
        projectDir = join(project, self.version, '$VARIANT')
        if self.env['PLATFORM'] == 'win32':
            libDir = [join(projectDir, 'lib')]
        else:
            libDir = [join(projectDir, 'lib'), join(projectDir, 'bin')]
        incDir = join(projectDir, 'include')
        self.env.Append(CPPPATH=incDir)
        self.env.Append(LIBPATH=libDir)
        self.env.Append(LIBS=name)


def UnitTestAction(target, source, env):
    pathvar = 'LD_LIBRARY_PATH'
    if env['PLATFORM'] == 'win32':
        pathvar = 'PATH'
    environ = env['ENV']
    if pathvar not in environ:
        environ[pathvar] = ''
    test = source[0].abspath
    options = '--gtest_output=xml:' + dirname(test) + os.sep
    for libpath in env['LIBPATH']:
        binpath = binPath(env.GetBuildPath(libpath))
        if isdir(binpath):
            environ[pathvar] += os.pathsep + binpath
    environ[pathvar] += os.pathsep + os.path.abspath(env.GetBuildPath('$BINDIR'))
    command = [test, options]
    mode = ARGUMENTS.get('mode', 'debug')
    mode = ARGUMENTS.get('with', mode)
    if mode == 'purify' or mode == 'quantify':
        purifytop = Popen([mode, '/printinstalldir'], stderr=PIPE).communicate()[1]
        environ[pathvar] += os.pathsep + join(os.path.dirname(purifytop), 'Common')
        save = '/run'
        if mode == 'quantify':
            save = '/savedata'
        command = [mode, save, test, options]
        env.Clean(test, withExtension(test, 'txt'))
    if mode == 'valgrind':
        valgrind = join(join(os.environ['VALGRIND_ROOT'], 'bin'), 'valgrind')
        valout = test + '.txt'
        command = [valgrind, '--leak-check=full', '--log-file=' + valout, test, options]
        env.Clean(test, valout)
    return call(command, env=environ)


@atexit.register
def __generate_reports():
    mode = ARGUMENTS.get('mode', 'debug')
    mode = ARGUMENTS.get('with', mode)
    if not GetOption('clean') and len(GetBuildFailures()) == 0:
        if mode == 'bullseye':
            __generate_bullseye_report()
        if mode == 'purify':
            __generate_purify_report()
        if mode == 'valgrind':
            __generate_valgrind_report()
        if mode == 'quantify':
            __generate_quantify_report()
        if mode == 'dox':
            __generate_doxygen()
    if mode == 'bullseye':  # remember to reset compiler in case of bullseye builds.
        call('cov01 --no-banner -0')


def __get_files_with_extension(ext):
    matches = []
    for (root, dirs, files) in os.walk('.'):
        for file in files:
            if file.endswith(ext):
                matches.append(os.path.join(root, file))
    return matches


def __generate_doxygen():
    doxygen = join(join(os.environ['DOXYGEN_ROOT'], 'bin'), 'doxygen')
    call([doxygen, 'Doxyfile'])


def __generate_bullseye_report():
    import csv
    csvout = []
    ignored = []
    if os.path.exists('.coverage_ignore'):
        with open('.coverage_ignore') as i:
            for line in i:
                ignored.append(line.strip())
    else:
        ignored.append('main(int,char*[])')
    for covfile in __get_files_with_extension('.cov'):
        dirname = os.path.basename(os.path.split(covfile)[0])
        dirname += '/main/'
        command = 'covfn --no-banner -n -k -u -c -f ' + covfile + ' ' + dirname
        pipe = Popen(command, stdout=PIPE)
        for line in pipe.communicate()[0].strip().split('\n'):
            csvout.append(line)
    output = []
    header = None
    for row in csv.reader(csvout):
        function = row[0]
        invoked = row[1] == '1'
        score = row[4]
        if function not in ignored:
            if len(score) == 0:
                if invoked:
                    score = '100%'
                else:
                    score = '0%'
            if score != '100%':
                output.append('{0:76}{1}'.format(function, score))
    if len(output) > 0:
        print '{0:_^80}'.format('[ Coverage Missing ]')
        print '{0:^80}'.format('')
        for o in output:
            print o
        print '{0:_^80}'.format('')
    else:
        print 'Good!'
    call('cov01 --no-banner -0')


def __generate_purify_report():
    import re
    ignore = []
    if os.path.exists('.purify_ignore'):
        with open('.purify_ignore') as i:
            for line in i:
                ignore.append(line.strip())
    for report in __get_files_with_extension('_test.txt'):
        failures = []
        test = os.path.basename(report).split('.')[0]
        with open(report) as f:
            for line in f:
                include = True
                if re.match("^\[[^I]\] .*", line):
                    for ignored in ignore:
                        include = include and not re.match(ignored, line)
                    if include:
                        failures.append(line.strip())
        if len(failures) > 0:
            print '{0:_^80}'.format('[ ' + test + ' ]')
            for failure in failures:
                print failure


def __generate_quantify_report():
    import re
    for report in __get_files_with_extension('_test.txt'):
        test = os.path.basename(report).split('.')[0]
        apptime = 'unknown'
        with open(report) as f:
            for line in f:
                if re.match("comment	Application Time .*", line):
                    apptime = line.split()[4]
                    break
        print '{0:_^42}'.format('[ Quantify run times ]')
        print '{0:<30}{1:>10}ms'.format(test, apptime)


def __generate_valgrind_report():
    import re
    for report in __get_files_with_extension('_test.txt'):
        test = os.path.basename(report).split('.')[0]
        summaries = []
        with open(report) as f:
            for line in f:
                if re.match('==.*== ERROR SUMMARY: [1-9].*', line):
                    summaries.append(line.strip())
        if len(summaries) > 0:
            print '{0:_^80}'.format('[ ' + test + ' ]')
            for summary in summaries:
                print summary


def protobuf_builder(target, source, env):
    protoc = env.GetBuildPath('$REPOSITORY/protobuf/$VARIANT/bin/protoc')
    environ = os.environ
    environ['LD_LIBRARY_PATH'] = env.GetBuildPath('$REPOSITORY/protobuf/$VARIANT/bin')
    for p in source:
        proto = p.srcnode().path
        outdir = dirname(dirname(dirname(dirname(str(target[0])))))
        cppout = '--cpp_out=' + outdir
        call([protoc, cppout, proto], env=environ)


def protobuf_emitter(target, source, env):
    outdir = target[0]
    del target[:]
    for s in source:
        module = os.path.splitext(s.srcnode().path)[0]
        target.extend([module + '.pb.cc', module + '.pb.h'])
    return (target, source)
