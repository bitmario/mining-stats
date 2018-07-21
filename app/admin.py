from django.contrib import admin
from solo.admin import SingletonModelAdmin

from . import models

admin.site.site_header = "MiningStats administration"


@admin.register(models.Rig)
class RigAdmin(admin.ModelAdmin):
    list_display = ("name", "host", "port", "enabled")
    list_filter = ("enabled", "port")
    search_fields = ["name", "host"]


class GpuStatusInline(admin.TabularInline):
    model = models.GpuStatus
    extra = 0


@admin.register(models.MinerStatus)
class MinerStatusAdmin(admin.ModelAdmin):
    inlines = [GpuStatusInline]
    readonly_fields = ("created_at",)
    list_display = ("miner", "created_at", "ping", "runtime", "gpus_online")
    list_filter = ("online", "miner__name", "created_at")


@admin.register(models.SiteConfiguration)
class SiteConfigurationAdmin(SingletonModelAdmin):
    pass
