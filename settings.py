# ...existing code...
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
# Ensure the directory exists
if not os.path.exists(STATICFILES_DIRS[0]):
    os.makedirs(STATICFILES_DIRS[0])
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# ...existing code...
