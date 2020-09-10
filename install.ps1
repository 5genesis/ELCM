$python=$args[0]

try {
    Write-Host Using (& $python --version)
} catch {
    Write-Host $_
    Write-Host Could not obtain Python version, please check script parameter. Aborting.
    exit
}

Write-Host Creating Virtualenv...
& $python -m venv ./venv

Write-Host Installing requirements...
& ./venv/Scripts/pip.exe install -r ./requirements.txt