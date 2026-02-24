from .models import ExpenseDocument
from .validators import validate_file

def attach_document(expense, document_type, file):
    validate_file(file)
    return ExpenseDocument.objects.create(
        expense=expense,
        document_type=document_type,
        file=file
    )
