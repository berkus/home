# remove aliases which i don't like
remove-item -path alias:diff -force
remove-item -path alias:rm -force
remove-item -path alias:cd
# perforce shortcuts
# show all open files
function po { p4 opened ... }
# show the changes to open files
function pd { p4 diff -dw ... }
# show 'dirty' files, i.e. files i've changed but not opened.
function dirty { p4 diff -se ... }
# open 'dirty' files
function open_dirty { foreach ($file in p4 diff -se ...) { p4 edit $file } }
# git shortcuts.
# show all open files
function go { git status -s }
# show the changes to open files
function gd { git diff HEAD }
# save changes back to github
function gsave { git push origin master }
# open a file in emacs
function open { c:\ajd\pkg\emacs\bin\emacsclientw.exe -c -n -a notepad $args[0] }
# run erlang programs from the shell
function erlang
{
    param($script)
    if($env:ERLANG_ROOT)
    {
        invoke-expression "$env:ERLANG_ROOT\bin\erlc.exe $script.erl"
        if($lastexitcode -eq "0")
        {
            invoke-expression "$env:ERLANG_ROOT\bin\erl.exe -noshell -s $script main $args"
        }
    }
}
# override cd to behave as i want
function cd
{
    switch ($args[0])
    {
        "-"   { $pwd=$AJD_OLDPWD }
        "a"   { $pwd="c:\ajd" }
        "t"   { $pwd="c:\ajd\tmp" }
        default { $pwd=$args[0] }
    }
    $tmp = pwd
    if($pwd) { set-location $pwd }
    set-variable -name AJD_OLDPWD -value $tmp -scope global
}
# setup visual studio compiler
function vc
{
    $env:vsinstalldir="c:\program files\microsoft visual studio 8"
    $env:vcinstalldir="c:\program files\microsoft visual studio 8\vc"
    $env:frameworkdir="c:\winnt\microsoft.net\framework"
    $env:frameworkversion="v2.0.50727"
    $env:frameworksdkdir="c:\program files\microsoft visual studio 8\sdk\v2.0"
    $env:devenvdir="c:\program files\microsoft visual studio 8\common7\ide"
    $oldpath=";$env:path"
    $env:path="c:\program files\microsoft visual studio 8\common7\ide"
    $env:path+=";c:\program files\microsoft visual studio 8\vc\bin"
    $env:path+=";c:\program files\microsoft visual studio 8\common7\tools"
    $env:path+=";c:\program files\microsoft visual studio 8\common7\tools\bin"
    $env:path+=";c:\program files\microsoft visual studio 8\vc\platformsdk\bin"
    $env:path+=";c:\program files\microsoft visual studio 8\sdk\v2.0\bin"
    $env:path+=";c:\winnt\microsoft.net\framework\v2.0.50727"
    $env:path+=";c:\program files\microsoft visual studio 8\vc\vcpackages"
    $env:path+=$oldpath
    $env:include+=";c:\program files\microsoft visual studio 8\vc\atlmfc\include"
    $env:include+=";c:\program files\microsoft visual studio 8\vc\include;"
    $env:include+=";c:\program files\microsoft visual studio 8\vc\platformsdk\include;"
    $env:include+=";c:\program files\microsoft visual studio 8\sdk\v2.0\include"
    $env:lib+=";c:\program files\microsoft visual studio 8\vc\atlmfc\lib"
    $env:lib+=";c:\program files\microsoft visual studio 8\vc\lib"
    $env:lib+=";c:\program files\microsoft visual studio 8\vc\platformsdk\lib"
    $env:lib+=";c:\program files\microsoft visual studio 8\sdk\v2.0\lib"
    $env:libpath="c:\winnt\microsoft.net\framework\v2.0.50727"
    $env:libpath+=";c:\program files\microsoft visual studio 8\vc\atlmfc\lib"
    set-variable -name AJD_BUILDSHELL -value "yes" -scope global
}
# quickly compile a test program
function vcc {cl /nologo /ehs /zi $args}

# pack/back up all the file i've changed
function pack
{
    $changedfiles=@()
    foreach($open in p4 opened ...)
    {
        $file = p4 where $open.split("#")[0]
        $changedfiles += $file.split(" ")[2]
    }
    if($changedfiles.length -gt 0)
    {
        $packdir = get-date -format yymmdhm
        new-item $packdir -itemtype directory -force > $null
        for($index=0; $index -lt $changedfiles.length; $index++)
        {
            copy-item $changedfiles[$index] -destination $packdir
        }
        write-host "packed changes to $packdir"
    }
}
# command prompt
function prompt
{
    $color="cyan"
    if($AJD_BUILDSHELL -eq "yes"){ $color="yellow" }
    write-host ("" + $(get-location) +" >") -nonewline -foregroundcolor $color
    $host.ui.rawui.windowtitle = $(get-location)
    return " "
}

# setup latest maven
function mvn3
{
    $env:M2="c:\ajd\pkg\maven"
    $env:M2_HOME="c:\ajd\pkg\maven"
    $env:PATH="c:\ajd\pkg\maven\bin;"+$env:PATH
}

# setup my environment variables
$env:SCONSFLAGS="-Q --site-dir=..\.scons"
$env:REPOSITORY="c:\ajd\pkg\repository"

# start in my home
set-location c:\ajd
