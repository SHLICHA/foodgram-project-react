from os import remove

from app.models import Ingredient
from django.contrib.auth import get_user_model
from django.http import HttpResponse

User = get_user_model()


def file_creation(shoping_list):
    """Формирование файла со списком покупок"""
    file_name = open("example.txt", "w+")
    for line_list in shoping_list:
        ingredient = Ingredient.objects.get(pk=line_list['ingredient'])
        file_name.write(f'{ingredient.name} '
                        f'({ingredient.measurement_unit})'
                        f' - {line_list["count"]}\n')
    file_name.close()
    read_file = open("example.txt", "r")
    response = HttpResponse(read_file.read(),
                            content_type="text/plain,charset=utf8"
                            )
    read_file.close()
    message = 'attachment; filename="{}.txt"'.format('file_name')
    response['Content-Disposition'] = message
    remove("example.txt")
    return response
