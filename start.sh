echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn..."
exec gunicorn Brio.wsgi --timeout 120 --limit-request-line 8190 --limit-request-field_size 8190 --worker-connections 1000

