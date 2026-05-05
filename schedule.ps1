
#TODO: finish this
function ifrunning{ #Checks if file is running
    $time = 0
    $quit = 0
    while ($true){
        $time -eq ($time + 1)
        if (!(Get-Process -Name notepad -ErrorAction SilentlyContinue)){
            Invoke-Item C:\Users\user\Desktop\ANPR-8-working\app.py #filename
        }
        elseif ($time -eq 900) {
            exit
        }
        else{
            Start-Sleep -Seconds 1
        }
    }
}

function timeChecker_normal #Mon-Thu Dismissal
{
    if ((($LocalTime.Hour) -eq 12) -and (($LocalTime.Minute) -eq 46)) {
        Invoke-Item C:\Users\user\Desktop\ANPR-8-working\app.py #filename
        ifrunning
        #Preschool 
    }
    elseif ((($LocalTime.Hour) -eq 14) -and (($LocalTime.Minute) -eq 25)) {
        Invoke-Item C:\Users\user\Desktop\ANPR-8-working\app.py #filename
        ifrunning
        #Year 1-2 
    }
    elseif ((($LocalTime.Hour) -eq 14) -and (($LocalTime.Minute) -eq 55)) {
        Invoke-Item C:\Users\user\Desktop\ANPR-8-working\app.py #filename
        ifrunning
        #Year 3-6 
    }
    elseif ((($LocalTime.Hour) -eq 15) -and (($LocalTime.Minute) -eq 15)) {
        Invoke-Item C:\Users\user\Desktop\ANPR-8-working\app.py #filename
        ifrunning
        #Secondary/Sixth Form
    }
    elseif ((($LocalTime.Hour) -eq 16) -and (($LocalTime.Minute) -eq 05)) {
        Invoke-Item C:\Users\user\Desktop\ANPR-8-working\app.py #filename
        ifrunning
        #CCA Combined
    }
    else{
        Start-Sleep -Seconds 60
    }
}

function timeChecker_short #Friday Dismissal
{
    if ((($LocalTime.Hour) -eq 11) -and (($LocalTime.Minute) -eq 55)) {
        Invoke-Item C:\Users\user\Desktop\ANPR-8-working\app.py #filename
        ifrunning
        #Preschool
    }
    elseif ((($LocalTime.Hour) -eq 11) -and (($LocalTime.Minute) -eq 55)) {
        Invoke-Item C:\Users\user\Desktop\ANPR-8-working\app.py #filename
        ifrunning
        #Year 1-2
    }
    elseif ((($LocalTime.Hour) -eq 12) -and (($LocalTime.Minute) -eq 25)) {
        Invoke-Item C:\Users\user\Desktop\ANPR-8-working\app.py #filename
        ifrunning
        #Year 3-6
    }
    elseif ((($LocalTime.Hour) -eq 12) -and (($LocalTime.Minute) -eq 55)) {
        Invoke-Item C:\Users\user\Desktop\ANPR-8-working\app.py #filename
        ifrunning
        #Secondary/Sixth Form
    }
    else{
        Start-Sleep -Seconds 60
    }
}

function day{
    Switch ($LocalTime.DayOfWeek)
    {
        5 {timeChecker_short}
        6 {Start-Sleep -Hours 1}
        7 {Start-Sleep -Hours 1}
        default {timeChecker_normal}
    }
    }
#Determines when students are scheduled to leave school

while ($true) {
    $LocalTime = Get-Date
    day
}
#Repeatedly gets current time from local server
