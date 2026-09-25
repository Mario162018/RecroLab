

$carpeta = Split-Path -Parent $MyInvocation.MyCommand.Path
$exe = Join-Path $carpeta "dist\RecreoLab.exe"
$icono = Join-Path $carpeta "dist\RecreoLab.ico"
$escritorio = [Environment]::GetFolderPath("Desktop")
$acceso = Join-Path $escritorio "RecreoLab.lnk"

if (Test-Path $exe) {
    $shell = New-Object -ComObject WScript.Shell
    $atajo = $shell.CreateShortcut($acceso)
    $atajo.TargetPath = $exe
    $atajo.WorkingDirectory = Join-Path $carpeta "dist"
    if (Test-Path $icono) {
        $atajo.IconLocation = $icono
    }
    $atajo.Save()
    Write-Host "Acceso directo creado en el Escritorio: RecreoLab"
} else {
    Write-Host "No se encontro dist\RecreoLab.exe -- no se pudo crear el acceso directo."
}
