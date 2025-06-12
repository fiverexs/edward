from django.db.models import Sum
from django.utils.timezone import localtime, make_aware
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from edward.models import PowerReading


def get_grouped_power_data(user, range_type="day", start_date=None, end_date=None):
    now = localtime()
    power_qs = PowerReading.objects.filter(user=user)

    if range_type == "hour":
        start = now - timedelta(hours=23)
        qs = power_qs.filter(timestamp__gte=start)
        buckets = [start + timedelta(hours=i) for i in range(24)]
        labels = [b.strftime("%Y-%m-%d %H:%M") for b in buckets]
        power1, power2 = [], []

        for b in buckets:
            e = qs.filter(timestamp__gte=b, timestamp__lt=b + timedelta(hours=1))
            agg = e.aggregate(p1=Sum("power1"), p2=Sum("power2"))
            power1.append(round(agg["p1"] or 0, 2))
            power2.append(round(agg["p2"] or 0, 2))

    elif range_type == "week":
        start = now - timedelta(days=6)
        qs = power_qs.filter(timestamp__date__gte=start.date())
        labels = [(start + timedelta(days=i)).strftime("%A") for i in range(7)]
        power1, power2 = [], []

        for i in range(7):
            day = (start + timedelta(days=i)).date()
            e = qs.filter(timestamp__date=day)
            agg = e.aggregate(p1=Sum("power1"), p2=Sum("power2"))
            power1.append(round(agg["p1"] or 0, 2))
            power2.append(round(agg["p2"] or 0, 2))

    elif range_type == "month":
        labels, power1, power2 = [], [], []

        # Safe date range parsing
        if start_date:
            try:
                start_dt = make_aware(datetime.strptime(start_date, "%Y-%m-%d"))
            except ValueError:
                start_dt = now - relativedelta(months=11)
        else:
            start_dt = now - relativedelta(months=11)

        if end_date:
            try:
                end_dt = make_aware(datetime.strptime(end_date, "%Y-%m-%d"))
            except ValueError:
                end_dt = now
        else:
            # Ensure we go to end of current month
            end_dt = now.replace(day=1) + relativedelta(months=1) - timedelta(seconds=1)

        current = start_dt.replace(day=1)

        while current <= end_dt:
            start = current
            end = current + relativedelta(months=1)
            label = current.strftime("%b %Y")

            qs = power_qs.filter(timestamp__gte=start, timestamp__lt=end)
            agg = qs.aggregate(p1=Sum("power1"), p2=Sum("power2"))

# Always include label even if 0 data
            labels.append(label)
            power1.append(round(agg.get("p1") or 0, 2))
            power2.append(round(agg.get("p2") or 0, 2))


            current = end

    else:
        labels, power1, power2 = [], [], []

    return {
        "labels": labels,
        "power1": power1,
        "power2": power2,
    }
