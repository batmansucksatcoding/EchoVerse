Write-Host "🌌 Setting up EchoVerse..."

# Create directories
Write-Host "📁 Creating directories..."
New-Item -ItemType Directory -Force -Path `
    "static/css","static/js","static/images",`
    "templates/journal","templates/dashboard","templates/insights","templates/visualizations","templates/registration",`
    "media/visualizations" | Out-Null

# Create migrations
Write-Host "🗄️  Creating database migrations..."
python manage.py makemigrations journal
python manage.py makemigrations emotions
python manage.py makemigrations visualizations
python manage.py makemigrations ai_insights

# Run migrations
Write-Host "🚀 Running migrations..."
python manage.py migrate

# Create superuser
Write-Host "👤 Create superuser account..."
python manage.py createsuperuser

# Collect static files
Write-Host "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Create cache table
python manage.py createcachetable

Write-Host ""
Write-Host "✅ Setup complete!"
Write-Host ""
Write-Host "To start the development server:"
Write-Host "  python manage.py runserver"
Write-Host ""
Write-Host "Access the app at: http://127.0.0.1:8123"
Write-Host "Admin panel at: http://127.0.0.1:8123/admin"
