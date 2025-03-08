@echo off
setlocal enabledelayedexpansion
set n=0
for /f "delims=" %%F in ('dir /b /a-d /od *.jpg') do (
    ren "%%F" "!n!.jpg"
    set /a n+=1
)
endlocal

setlocal enabledelayedexpansion
set n=0
for /f "delims=" %%F in ('dir /b /a-d /od *.png') do (
    ren "%%F" "!n!.png"
    set /a n+=1
)
endlocal

setlocal enabledelayedexpansion
set n=0
for /f "delims=" %%F in ('dir /b /a-d /od *.gif') do (
    ren "%%F" "!n!.gif"
    set /a n+=1
)
endlocal

setlocal enabledelayedexpansion
set n=0
for /f "delims=" %%F in ('dir /b /a-d /od *.mp4') do (
    ren "%%F" "!n!.mp4"
    set /a n+=1
)
endlocal

setlocal enabledelayedexpansion
set n=0
for /f "delims=" %%F in ('dir /b /a-d /od *.webp') do (
    ren "%%F" "!n!.webp"
    set /a n+=1
)
endlocal