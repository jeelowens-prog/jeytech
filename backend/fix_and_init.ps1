# Script PowerShell pour corriger et initialiser la base de données

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Correction et Initialisation DB" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Désinstaller passlib si présent
Write-Host "Désinstallation de passlib..." -ForegroundColor Yellow
pip uninstall -y passlib 2>$null

# Installer bcrypt directement
Write-Host "Installation de bcrypt..." -ForegroundColor Yellow
pip install bcrypt==4.0.1

# Réinstaller toutes les dépendances
Write-Host "Réinstallation des dépendances..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "Suppression de l'ancienne base de données..." -ForegroundColor Yellow
if (Test-Path "jerrytech.db") {
    Remove-Item "jerrytech.db" -Force
    Write-Host "✓ Base de données supprimée" -ForegroundColor Green
}

Write-Host ""
Write-Host "Initialisation de la nouvelle base de données..." -ForegroundColor Yellow
python init_db.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Initialisation réussie!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Vous pouvez maintenant démarrer le serveur avec:" -ForegroundColor Cyan
    Write-Host "  python main.py" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "❌ Erreur lors de l'initialisation" -ForegroundColor Red
    Write-Host "Vérifiez les messages d'erreur ci-dessus" -ForegroundColor Yellow
}

Write-Host ""

