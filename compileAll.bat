REM python pl0parser.py ..\testfiles\tmin.pl0
@echo off
    for /R "..\testfiles\" %%f in (tmin*.pl0) do (
    echo Compile %%~nf
    python cpl0.py %%f
)