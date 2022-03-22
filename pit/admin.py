from django import forms
from django.contrib import admin
from .models import Sala, Equipo, Mesa, Slot, Reserva

class CsvImportForm(forms.Form):
    csv_file = forms.FileField()
    descripcion = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4, "cols": 50}),
        label=''
    )

from django.shortcuts import render, redirect

class HeroAdmin(admin.ModelAdmin):

    change_list_template = "pit/admin/importa_lista_equipos.html"



    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            #reader = csv.reader(csv_file)
            # Create Hero objects from passed in data
            # ...
            self.message_user(request, "Your csv file has been imported")
            return redirect("..")
        payload = {"form": CsvImportForm(), "paco": "manolo"}
        return render(
            request, "pit/admin/importa_lista_equipos.html", payload
        )

admin.site.register(Sala)
admin.site.register(Equipo)
admin.site.register(Mesa)
# admin.site.register(Slot, HeroAdmin)
admin.site.register(Slot)
admin.site.register(Reserva)