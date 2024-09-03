from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .models import Bike, BikeModel, BikeBrand

class BikeBrandAdmin(ImportExportModelAdmin):
    pass  # Если нет дополнительных настроек, используйте pass

class BikeModelAdmin(ImportExportModelAdmin):
    pass  # Если нет дополнительных настроек, используйте pass

class BikeAdmin(ImportExportModelAdmin):
    pass  # Если нет дополнительных настроек, используйте pass

# Register your models here.
admin.site.register(Bike, BikeAdmin)
admin.site.register(BikeModel, BikeModelAdmin)
admin.site.register(BikeBrand, BikeBrandAdmin)
