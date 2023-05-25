from django.forms import ModelForm
from .models import IngredientsImport


class IngredientsImportForm(ModelForm):
    class Meta:
        model = IngredientsImport
        fields = ('csv_file',)
