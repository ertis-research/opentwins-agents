# Crea la carpeta local donde se guardarán los backups
$backupDir = ".\backup"
New-Item -ItemType Directory -Force -Path $backupDir

# Lista pods y filtra los que contienen 'receptor'
$pods = kubectl get pods -o name | Where-Object { $_ -match "receptor" }

foreach ($pod in $pods) {
    # Extrae solo el nombre (quita el prefijo 'pod/')
    $podName = ($pod -split "/")[1]

    Write-Host "Copiando de $podName..."
    kubectl cp "opentwins/${podName}:/app" "$backupDir\$podName"
}