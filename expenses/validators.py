from django.core.exceptions import ValidationError

ALLOWED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png', 'docx']
MAX_FILE_SIZE_MB = 5

def validate_file(file):
    ext = file.name.split('.')[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError("Unsupported file format.")

    if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValidationError("File size exceeds 5MB.")
