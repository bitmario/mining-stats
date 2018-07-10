from datetime import timedelta

from django.db import models
from django.core.validators import MaxValueValidator
from django.utils.translation import ugettext as _
from solo.models import SingletonModel

from . import miners


MINER_CLAYMORE = 'claymore'
MINER_TYPES = (
    (MINER_CLAYMORE, _('Claymore')),
)

class Rig(models.Model):
    type = models.CharField(_('miner type'), max_length=10, choices=MINER_TYPES, 
                            default=MINER_CLAYMORE)
    host = models.CharField(_('hostname/IP'), max_length=255)
    port = models.PositiveIntegerField(_('port'), validators=[MaxValueValidator(65535)])
    password = models.CharField(_('password'), max_length=60, blank=True)
    name = models.CharField(_('display name'), max_length=50, db_index=True)
    active_gpus = models.PositiveSmallIntegerField(_('# of active GPUs'), default=6)
    enabled = models.BooleanField(_('monitoring enabled'), default=True)

    class Meta:
        verbose_name = _('rig')
        verbose_name_plural = _('rigs')
        unique_together = ('host', 'port')
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_last_status(self):
        try:
            return MinerStatus.objects.filter(miner=self).order_by('-pk')[0]
        except:
            return None

    def get_claymore(self):
        return miners.Claymore(self.host, self.port, self.password)


class MinerStatusManager(models.Manager):
    def create(self, *args, **kwargs):
        if 'stats' in kwargs and isinstance(kwargs['stats'], miners.Stats):
            stats = kwargs['stats']
            del kwargs['stats']
            kwargs['miner'] = Rig.objects.get(host=stats.miner.host, port=stats.miner.port)
            kwargs['ping'] = stats.ping
            kwargs['online'] = stats.online
            kwargs['error'] = stats.error
            if stats.online:
                kwargs['version'] = stats.version
                kwargs['runtime'] = stats.runtime
                kwargs['hashrate'] = stats.hashrate
                kwargs['shares'] = stats.shares
                kwargs['rej_shares'] = stats.rej_shares
                kwargs['pool'] = stats.pool
                kwargs['invalid_shares'] = stats.invalid_shares
                kwargs['pool_switches'] = stats.pool_switches
                kwargs['gpus_online'] = stats.gpus_online
                kwargs['gpus_offline'] = stats.gpus_offline
                kwargs['max_temp'] = stats.max_temp
            s = super(MinerStatusManager, self).create(*args, **kwargs)
            for g in stats.gpus:
                GpuStatus.objects.create(miner_status=s, number=g.number, 
                                         hashrate=g.hashrate, temp=g.temp, fan=g.fan)
        else:
            super(MinerStatusManager, self).create(*args, **kwargs)
        

class MinerStatus(models.Model):
    objects = MinerStatusManager()

    miner = models.ForeignKey(Rig, verbose_name=_('rig'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True, db_index=True)
    online = models.BooleanField(_('online'), default=False)
    error = models.CharField(_('error'), max_length=512, blank=True, null=True, default=None)
    ping = models.PositiveSmallIntegerField(_('ping (ms)'), blank=True, null=True)
    version = models.CharField(_('version'), max_length=255, blank=True)
    runtime = models.IntegerField(_('uptime (mins)'), blank=True, null=True)
    hashrate = models.DecimalField(_('hashrate (MH/s)'), max_digits=9, decimal_places=3, 
                                   blank=True, null=True)
    shares = models.IntegerField(_('shares'), blank=True, null=True)
    rej_shares = models.IntegerField(_('rejected shares'), blank=True, null=True)
    pool = models.CharField(_('pool'), max_length=255, blank=True)
    invalid_shares = models.IntegerField(_('invalid shares'), blank=True, null=True)
    pool_switches = models.IntegerField(_('pool switches'), blank=True, null=True)
    gpus_online = models.IntegerField(_('GPUs online'), blank=True, null=True)
    gpus_offline = models.IntegerField(_('GPUs offline'), blank=True, null=True)
    max_temp = models.IntegerField(_('max GPU temp'), blank=True, null=True)

    @property
    def runtime_pretty(self):
        return str(timedelta(minutes=self.runtime))[:-3]

    @property
    def created_pretty(self):
        return '{:%Y-%m-%d %H:%M}'.format(self.created_at)

    class Meta:
        verbose_name = _('miner status')
        verbose_name_plural = _('miner statuses')
        ordering = ['-created_at', 'miner']
        indexes = [
            models.Index(fields=['miner', 'created_at']),
        ]


class GpuStatus(models.Model):
    miner_status = models.ForeignKey(MinerStatus, verbose_name=_('miner status record'),
                                     related_name='gpus', on_delete=models.CASCADE)
    number = models.SmallIntegerField(_('GPU no.'))
    hashrate = models.DecimalField(_('hashrate (MH/s)'), max_digits=9, decimal_places=3)
    temp = models.SmallIntegerField(_('temperature (C)'))
    fan = models.SmallIntegerField(_('fan (%)'))

    class Meta:
        verbose_name = _('GPU status')
        verbose_name_plural = _('GPU statuses')
        indexes = [models.Index(fields=['miner_status', 'number'])]
        ordering = ['-miner_status', 'number']


class SiteConfiguration(SingletonModel):
    restrict_stats = models.BooleanField(_('restrict stats?'), default=False,
                                         help_text=_('restrict stats viewing to logged in users'))
    restrict_actions = models.BooleanField(_('restrict actions?'), default=True,
                                           help_text=_('restrict actions (restart, etc.) to logged in users'))
    warn_temp = models.PositiveIntegerField(_('warning temperature'), default=55,
                                            help_text=_('value above which stats are displayed in yellow'))
    danger_temp = models.PositiveIntegerField(_('danger temperature'), default=70,
                                            help_text=_('value above which stats are displayed in red'))
    warn_fan = models.PositiveIntegerField(_('warning fan %'), default=60,
                                            help_text=_('value above which stats are displayed in yellow'))
    danger_fan = models.PositiveIntegerField(_('danger fan %'), default=75,
                                            help_text=_('value above which stats are displayed in red'))

    def __str__(self):
        return str(("site configuration"))

    class Meta:
        verbose_name = _("site configuration")
