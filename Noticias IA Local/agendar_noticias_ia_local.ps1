param(
    [string]$PythonwPath = "C:\Users\saulo\AppData\Local\Programs\Python\Python312\pythonw.exe",
    [string]$ScriptPath = "C:\Users\saulo\OneDrive\Documentos\01 - Pessoal\03 Estudo e Carreira\Python\Scripts\Noticias IA Local\gerar_noticias_ia_txt.py",
    [string]$TaskName = "Noticias IA Local",
    [string]$StartTime = "08:00"
)

$action = New-ScheduledTaskAction -Execute $PythonwPath -Argument "`"$ScriptPath`""
$trigger = New-ScheduledTaskTrigger -Daily -At $StartTime
$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 15)

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Gera diariamente um arquivo TXT local com noticias sobre IA." `
    -Force
