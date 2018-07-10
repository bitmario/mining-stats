from django_cron import CronJobBase, Schedule

from . import models
from . import miners


class UpdateStats(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.update_stats'

    def do(self):
        rigs = models.Rig.objects.all()
        for r in rigs:
            if not r.enabled:
                continue
            m = r.get_claymore()
            models.MinerStatus.objects.create(stats=m.get_stats())
