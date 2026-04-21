param(
    [string]$PythonwPath = "C:\Users\saulo\AppData\Local\Programs\Python\Python312\pythonw.exe",
    [string]$ScriptPath = "C:\Users\saulo\OneDrive\Documentos\01 - Pessoal\03 Estudo e Carreira\Python\Scripts\Email Profissional\Noticias IA Diarias\enviar_noticias_ia.py",
    [string]$TaskName = "Noticias IA Diarias",
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
    -Description "Envia diariamente um resumo por e-mail com noticias sobre IA." `
    -Force
