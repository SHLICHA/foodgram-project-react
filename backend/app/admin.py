import csv

from django.contrib import admin, messages
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import IngredientsImportForm
from .models import (
    CountIngredients,
    Recipe,
    Tag,
    Ingredient,
    IngredientsImport,
)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author',)
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)

    def get_urls(self):
        urls = super().get_urls()
        urls.insert(-1, path('csv-upload/', self.upload_csv))
        return urls

    def upload_csv(self, request):
        if request.method == 'POST':
            form = IngredientsImportForm(request.POST, request.FILES)
            if form.is_valid():
                # реализация обработки формы
                form_object = form.save()
                with form_object.csv_file.open('r') as csv_file:
                    rows = csv.reader(csv_file, delimiter=',')
                    for row in rows:
                        Ingredient.objects.update_or_create(
                           name=row[0],
                           measurement_unit=row[1]
                        )
                url = reverse('admin:index')
                messages.success(request, 'Файл успешно импортирован')
                return HttpResponseRedirect(url)
        form = IngredientsImportForm()
        return render(request, 'admin/csv_import_page.html', {'form': form})


@admin.register(IngredientsImport)
class IngredientsImportAdmin(admin.ModelAdmin):
    list_display = ('csv_file', 'date_added',)


@admin.register(CountIngredients)
class CountIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')


admin.site.register(Tag)
