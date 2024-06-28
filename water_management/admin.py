from django.contrib import admin
from .models import *

admin.site.register(Person)
admin.site.register(Contractor)
admin.site.register(GramPanchayat)
admin.site.register(WaterUserCommittee)
admin.site.register(Pipeline)
admin.site.register(PumpOperator)
admin.site.register(WaterQuality)
admin.site.register(SupplyFrequency)
admin.site.register(Maintenance)
admin.site.register(FeeCollection)
admin.site.register(FeeRate)
admin.site.register(TimeEntry)