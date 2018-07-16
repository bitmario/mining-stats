"""
Definition of views.
"""
from datetime import timedelta
import json

from django.shortcuts import render, redirect, render_to_response
from django.http import HttpRequest, Http404, HttpResponseBadRequest
from django.template import RequestContext
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import numpy as np
import pandas as pd

from . import models


def stats(request):
    """Renders the stats page."""
    assert isinstance(request, HttpRequest)

    config = models.SiteConfiguration.get_solo()
    if config.restrict_stats and not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    rigs = models.Rig.objects.all()
    miner_stats = []
    for r in rigs:
        if not r.enabled:
            continue
        s = r.get_last_status()
        if s is not None:
            miner_stats.append(s)

    miner_stats = sorted(miner_stats, key=lambda x: (x.online, x.miner.host))
    total_hashrate = sum(0 if s.hashrate is None else s.hashrate for s in miner_stats)
    rigs_online = sum(1 if s.online else 0 for s in miner_stats)
    rigs_offline = len(miner_stats) - rigs_online
    gpus_online = sum(0 if s.gpus_online is None else s.gpus_online for s in miner_stats)
    gpus_offline = sum(0 if s.gpus_offline is None else s.gpus_offline for s in miner_stats)

    if len(miner_stats) > 0:
        max_temp = max(0 if s.max_temp is None else s.max_temp for s in miner_stats)
        max_dt = max(s.created_at for s in miner_stats)
    else:
        max_temp = 0
        max_dt = 0

    title = 'Overview at {:%Y-%m-%d %H:%M}'.format(timezone.localtime(max_dt)) if len(miner_stats) > 0 else 'No rigs configured'

    return render(
        request,
        'app/stats.html',
        {
            'config': config,
            'title': title,
            'stats': miner_stats,
            'total_hashrate': total_hashrate,
            'rigs_online': rigs_online,
            'rigs_offline': rigs_offline,
            'gpus_online': gpus_online,
            'gpus_offline': gpus_offline,
            'max_temp': max_temp,
        }
    )

def restart(request, rig_id):
    """Restarts a rig"""
    assert isinstance(request, HttpRequest)

    config = models.SiteConfiguration.get_solo()
    if config.restrict_actions and not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    try:
        r = models.Rig.objects.get(pk=rig_id)
        r.get_claymore().restart()
    except models.Rig.DoesNotExist:
        return Http404("Rig does not exist")
    return render(
        request, 
        'app/operation_success.html', 
        {
            'config': config,
            'title': 'Success!', 
            'rig': r, 
            'operation':'restart'
        }
    )

def reboot(request, rig_id):
    """Reboots a rig"""
    assert isinstance(request, HttpRequest)

    config = models.SiteConfiguration.get_solo()
    if config.restrict_actions and not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    try:
        r = models.Rig.objects.get(pk=rig_id)
        r.get_claymore().reboot()
    except models.Rig.DoesNotExist:
        return Http404("Rig does not exist")
    return render(
        request, 
        'app/operation_success.html', 
        {
            'config': config,
            'title': 'Success!',
            'rig': r,
            'operation':'reboot'
        }
    )

def chart(request, rig_id=None, hours=None):
    assert isinstance(request, HttpRequest)

    config = models.SiteConfiguration.get_solo()
    if config.restrict_actions and not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    default_hours = 24
    max_hours = 7 * 24
    if hours is None:
        hours = default_hours
    else:
        hours = int(hours)
        if hours < 1 or hours > max_hours:
            hours = default_hours

    try:
        rig = models.Rig.objects.get(pk=rig_id)
    except models.Rig.DoesNotExist:
        return Http404("Rig does not exist")

    if hours > 24:
        mins = 60
        time_unit = 'day'
    elif hours > 12:
        mins = 30
        time_unit = 'hour'
    elif hours > 2:
        mins = 10
        time_unit = 'minute'
    else:
        mins = 5
        time_unit = 'minute'
    
    date_from = timezone.now() - timedelta(hours=hours)
    query = models.MinerStatus.objects \
                              .filter(miner__id=rig_id, created_at__gte=date_from) \
                              .order_by('id')

    has_data = query and query.filter(online=True).exists()

    if has_data:
        dates = [timezone.localtime(x.created_at) for x in query]
        hashrates = [float(x.hashrate) if x.hashrate is not None else x.hashrate for x in query]
        temps = [int(x.max_temp) if x.hashrate is not None else x.hashrate for x in query]

        df = pd.DataFrame({'hashrate': hashrates, 'temp': temps}, dates)
        dft = df.resample('{}T'.format(mins)).agg([np.mean, np.min, np.max, np.std]).round(2)

        dates = json.dumps(['{:%Y-%m-%d %H:%M}'.format(x) for x in dft.index.to_pydatetime().tolist()])
        hashrates = json.dumps(dft['hashrate']['mean'].values.tolist())
        temps = json.dumps(dft['temp']['mean'].values.tolist())

        gpu_query = models.GpuStatus.objects \
                                    .filter(miner_status_id__in=[x.pk for x in query])
        gpu_numbers = []
        gpu_hashrates = []
        gpu_temps = []
        for g in gpu_query:
            gpu_numbers.append(int(g.number))
            gpu_hashrates.append(float(g.hashrate))
            gpu_temps.append(int(g.temp))
        gpu_df = pd.DataFrame({'hashrate': gpu_hashrates, 'temp': gpu_temps}, gpu_numbers)
        gpu_dft = gpu_df.groupby(gpu_df.index).agg([np.mean, np.max]).round(3)
        gpu_numbers = [int(x) for x in gpu_dft.index.tolist()]
        gpu_hashrates = json.dumps(gpu_dft['hashrate']['mean'].values.tolist())
        gpu_temps = json.dumps(gpu_dft['temp']['amax'].values.tolist())
    else:
        dates = None
        hashrates = None
        temps = None
        gpu_numbers = None
        gpu_hashrates = None
        gpu_temps = None
    
    return render(
        request, 
        'app/charts.html',
        {
            'title': 'Charts for {} ({}:{})'.format(rig.name, rig.host, rig.port),
            'miner': rig,
            'time_unit': time_unit,
            'hours': hours,
            'mins': mins,
            'has_data': has_data,
            'dates': dates,
            'hashrates': hashrates,
            'temps': temps,
            'gpu_numbers': gpu_numbers,
            'gpu_hashrates': gpu_hashrates,
            'gpu_temps': gpu_temps,
        }
    )
