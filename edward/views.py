from .models import Contact,BannerImage, Headline, Paragraph, Profile, PageView, Session, Post, Comment,WebsiteConfiguration, Contact,EnergyUsage ,ArchivedContact, Notification, AdminMessage, PendingWork,EnergyConsumption,RealTimeEnergyData,PowerReading
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.contrib.auth.models import User
import json, csv 
import requests
from django.db import IntegrityError
from django.db.models import Avg, F, Sum
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import  UpdateUserForm, UpdatePasswordForm, PasswordChangeForm ,PendingWorkForm,ClientSignUpForm,AdminCreateUserForm,ClientCreationForm
from django.contrib.auth import authenticate, login,logout, update_session_auth_hash, get_user_model
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count, Avg
from django.db.models.functions import TruncMinute, TruncHour, TruncDay, TruncWeek, TruncMonth
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.utils.timezone import now, timedelta,make_aware,get_current_timezone_name, localtime, localdate
from django.utils.dateparse import parse_date
from django.http import JsonResponse
from django.core.mail import send_mail
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict
from django.template.loader import get_template
from xhtml2pdf import pisa
import io
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from edward.utils.aggregations import get_grouped_power_data
from django.core.paginator import Paginator

today = now().replace(hour=0, minute=0, second=0, microsecond=0)
end_of_today = today + timedelta(days=1)

def home(request):
    # Retrieve content for the home page
    banner_image = BannerImage.objects.first()
    headline = Headline.objects.first()
    paragraph = Paragraph.objects.first()

    # Retrieve or create the website configuration
    config, created = WebsiteConfiguration.objects.get_or_create(
        id=1,  # Ensure only a single instance
        defaults={
            'site_name': "5RS Construction Services",
            'contact_email': "fiversconstruction@yahoo.com",
            'contact_phone': "09089074031",
            'address': "Bayanan, Bacoor Cavite",
            'facebook_page': "https://www.facebook.com/5rsconstruction",
            'footer_text': "Copyright © 2024 All Rights Reserved.",
        }
    )

    if request.method == 'POST':
        # Process form data if POST request
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        # Check if all fields are filled in
        if not (name and email and phone and message):
            # Show error and re-render the page with existing input values
            messages.error(request, "All fields are required!")
            return render(request, 'home.html', {
                'banner_image': banner_image,
                'headline': headline,
                'paragraph': paragraph,
                'config': config,
                'name': name,
                'email': email,
                'phone': phone,
                'message': message,
            })

        # Save the contact information if all fields are filled
        contact = Contact(name=name, email=email, phone=phone, message=message)
        contact.save()
        
        # Add a success message and redirect with a URL parameter to trigger the modal
        messages.success(request, "Your message has been successfully sent!")
        return redirect('/?submitted=True')

    # Context for GET request
    context = {
        'banner_image': banner_image,
        'headline': headline,
        'paragraph': paragraph,
        'config': config,
    }

    return render(request, 'home.html', context)


def delete_contact(request, contact_id):
    # Retrieve the contact submission or return a 404 error if not found
    contact = get_object_or_404(Contact, id=contact_id)

    # Move the contact details to the archive
    ArchivedContact.objects.create(
        name=contact.name,
        email=contact.email,
        phone=contact.phone,
        message=contact.message,
        created_at=contact.created_at
    )

    # Delete the original contact submission
    contact.delete()

    # Display a success message
    messages.success(request, "Contact submission has been deleted and archived.")

    # Redirect back to the dashboard or contact submissions page
    return redirect('contact_submissions_page')  # Adjust this to your specific URL name

@never_cache
@login_required(login_url='/login/')
def archived_contacts(request):
    # Get all archived contacts, ordered by the date they were archived
    archived_contacts = ArchivedContact.objects.order_by('-archived_at')

    context = {
        'archived_contacts': archived_contacts,
    }

    return render(request, 'archived_contacts.html', context)

def delete_all_archived_contacts(request):
    if request.method == 'POST':  # Ensure the action is triggered only via POST
        ArchivedContact.objects.all().delete()
        messages.success(request, 'All archived contacts have been permanently deleted.')
    return redirect('archived_contacts')  # Redirect to the archived contacts page



def index(request):
    config = WebsiteConfig.objects.first()  # Assuming there's only one configuration entry
    return render(request, 'index.html', {'config': config})

def custom_logout(request):
    logout(request)
    return redirect('home')

def login_selection(request):
    return render(request, 'login_selection.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if the user is an admin (staff or superuser)
            if user.is_staff or user.is_superuser:
                messages.error(request, 'Admins are not allowed to log in from this page.')
                return redirect('user_login')  # Redirect to Django's admin login page if admin
            else:
                # Log in regular user (non-admin)
                login(request, user)
                return redirect('user_dashboard')  # Redirect to user dashboard after login
        else:
            # Show an error if authentication failed
            messages.error(request, "Invalid username or password.", extra_tags='user')

    
    return render(request, 'user_login.html')
    
def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')  # Redirect to admin dashboard
        else:
           messages.error(request, "Invalid username or password.", extra_tags='admin')

    
    return render(request, 'admin_login.html')

def create_client_account(request): 
    if request.method == 'POST':
        form = ClientSignUpForm(request.POST)
        if form.is_valid():
            form.save()  # 👈 don't log in
            messages.success(request, '✅ Account created successfully! Please log in.')
            return redirect('user_login')  # make sure this name matches your URLconf
    else:
        form = ClientSignUpForm()
    return render(request, 'create_client_account.html', {'form': form})

def create_admin_account(request):
    if request.method == 'POST':
        form = AdminCreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_management')
    else:
        form = AdminCreateUserForm()
    return render(request, 'add_user.html', {'form': form})

def terms_conditions(request):
    return render(request, 'terms_conditions.html')

@never_cache
@login_required(login_url='/login/')
def user_dashboard(request):
    user  = request.user
    today = timezone.localdate()
    week_start = today - timedelta(days=6)
    month_start = today.replace(day=1)

    # ——————————————————————————————————————————————————————
    # 1) TODAY total (persisted if available, else live sum)
    # ——————————————————————————————————————————————————————
    usage_today = EnergyUsage.objects.filter(user=user, date=today).first()
    if usage_today:
        total_today = float(usage_today.energy_consumed)
    else:
        # sum live readings for today
        agg = PowerReading.objects.filter(
            user=user, timestamp__date=today
        ).aggregate(t=Sum('power1') + Sum('power2'))
        total_today = agg['t'] or 0

    # ——————————————————————————————————————————————————————
    # 2) THIS WEEK total
    # ——————————————————————————————————————————————————————
    # sum up any daily records we have...
    week_sum = EnergyUsage.objects.filter(
        user=user, date__gte=week_start, date__lte=today
    ).aggregate(s=Sum('energy_consumed'))['s'] or 0

    # ...plus live readings from days we haven’t recorded yet (including today)
    missing_days = [
        d for d in (week_start + timedelta(i) for i in range(7))
        if not EnergyUsage.objects.filter(user=user, date=d).exists()
    ]
    live_sum = PowerReading.objects.filter(
        user=user, timestamp__date__in=missing_days
    ).aggregate(t=Sum('power1') + Sum('power2'))['t'] or 0

    total_week = week_sum + live_sum

    # ——————————————————————————————————————————————————————
    # 3) THIS MONTH total
    # ——————————————————————————————————————————————————————
    month_sum = EnergyUsage.objects.filter(
        user=user,
        date__year=today.year,
        date__month=today.month
    ).aggregate(s=Sum('energy_consumed'))['s'] or 0

    # live for days without a record
    days_in_month = (today.day)
    month_missing = [
        today.replace(day=d)
        for d in range(1, days_in_month+1)
        if not EnergyUsage.objects.filter(user=user, date__day=d,
                                           date__month=today.month,
                                           date__year=today.year).exists()
    ]
    live_month = PowerReading.objects.filter(
        user=user, timestamp__date__in=month_missing
    ).aggregate(t=Sum('power1') + Sum('power2'))['t'] or 0

    total_month = month_sum + live_month

    # ——————————————————————————————————————————————————————
    # 4) BUILD 7-DAY HISTORY FOR CHART (using live for missing days)
    # ——————————————————————————————————————————————————————
    history = []
    for d in (week_start + timedelta(i) for i in range(7)):
        eu = EnergyUsage.objects.filter(user=user, date=d).first()
        if eu:
            history.append(float(eu.energy_consumed))
        else:
            # live sum for that day
            agg = PowerReading.objects.filter(
                user=user, timestamp__date=d
            ).aggregate(t=Sum('power1') + Sum('power2'))['t'] or 0
            history.append(agg)

    history_labels = [(week_start + timedelta(i)).strftime("%b %d") for i in range(7)]

    # ——————————————————————————————————————————————————————
    # 5) ADMIN / NOTIFICATIONS / CONTACTS / DEVICES
    # ——————————————————————————————————————————————————————
    admin_messages = AdminMessage.objects.all().order_by('-created_at')[:5]
    notifications  = Notification.objects.filter(user=user).order_by('-created_at')
    unread_count   = notifications.filter(is_read=False).count()
    user_contacts  = Contact.objects.filter(email=user.email).order_by('-created_at')

    # device count still from live readings today
    power_logs_today   = PowerReading.objects.filter(user=user, timestamp__date=today)
    connected_devices = (
        power_logs_today.filter(power1__gt=0).exists() +
        power_logs_today.filter(power2__gt=0).exists()
    )

    context = {
        # summary tiles
        'total_power_today':   round(total_today,   2),
        'total_power_week':    round(total_week,    2),
        'total_power_month':   round(total_month,   2),

        # 7-day history
        'history_labels': history_labels,
        'history_data'  : history,

        # other UI pieces
        'admin_messages':    admin_messages,
        'notifications':     notifications,
        'unread_count':      unread_count,
        'user_contacts':     user_contacts,
        'connected_devices': connected_devices,
        
    }

    return render(request, 'user_dashboard.html', context)

def get_today_range():
    start = localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    return start, start + timedelta(days=1)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def filtered_dashboard_data(request):
    user = request.user
    start_str = request.GET.get("start")
    end_str = request.GET.get("end")

    if not start_str or not end_str:
        return Response({"error": "Start and end dates are required."}, status=400)

    try:
        start = make_aware(datetime.strptime(start_str, "%Y-%m-%d"))
        end = make_aware(datetime.strptime(end_str, "%Y-%m-%d")) + timedelta(days=1)
    except ValueError:
        return Response({"error": "Invalid date format."}, status=400)

    qs = PowerReading.objects.filter(user=user, timestamp__range=(start, end))

    total_power1 = qs.aggregate(s=Sum("power1"))["s"] or 0
    total_power2 = qs.aggregate(s=Sum("power2"))["s"] or 0

    return Response({
        "start": start_str,
        "end": end_str,
        "total_power1": round(total_power1, 2),
        "total_power2": round(total_power2, 2)
    })


@csrf_exempt
def sensor_endpoint(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Extract values from JSON
            voltage = data.get("voltage")
            current = data.get("current")
            user_id = data.get("user_id")  # optional: based on how you associate

            # You must assign a user – here we use the first superuser as fallback
            from django.contrib.auth.models import User
            user = User.objects.filter(is_superuser=True).first()

            # Save to PowerReading model
            PowerReading.objects.create(
                user=user,
                power1=voltage,
                power2=current,
                timestamp=now()
            )

            return JsonResponse({"status": "OK", "message": "Reading saved"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "invalid request"}, status=405)


@login_required
def historical_power_data(request):
    user = request.user
    now = localtime()
    start = now - timedelta(hours=23)
    readings = PowerReading.objects.filter(user=user, timestamp__gte=start).order_by("timestamp")

    timestamps = [localtime(r.timestamp).strftime("%Y-%m-%d %H:%M:%S") for r in readings]
    power1 = [float(r.power1) for r in readings]
    power2 = [float(r.power2) for r in readings]

    return JsonResponse({
        "timestamps": timestamps,
        "power1": power1,
        "power2": power2
    })

@login_required
def live_energy_totals(request):
    user = request.user
    now = localtime()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())  # Monday
    month_start = today_start.replace(day=1)

    def total(qs, field):
        agg = qs.aggregate(total=Sum(field))
        return agg["total"] or 0

    today_qs = PowerReading.objects.filter(user=user, timestamp__gte=today_start)
    week_qs = PowerReading.objects.filter(user=user, timestamp__gte=week_start)
    month_qs = PowerReading.objects.filter(user=user, timestamp__gte=month_start)

    today_total = total(today_qs, "power1") + total(today_qs, "power2")
    week_total = total(week_qs, "power1") + total(week_qs, "power2")
    month_total = total(month_qs, "power1") + total(month_qs, "power2")

    # ✅ fallback to today if only today's data exists
    if week_total == 0 and today_total > 0:
        week_total = today_total
    if month_total == 0 and today_total > 0:
        month_total = today_total

    return JsonResponse({
        "today": round(today_total, 2),
        "week": round(week_total, 2),
        "month": round(month_total, 2),
    })

@csrf_exempt
def save_power_reading(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            power1 = float(data.get("power1", 0))
            power2 = float(data.get("power2", 0))

            # Use request.user if authenticated — here we fallback to the first user
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = request.user if request.user.is_authenticated else User.objects.first()

            PowerReading.objects.create(
                user=user,
                power1=power1,
                power2=power2,
                timestamp=now()
            )
            return JsonResponse({"status": "saved"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "POST only"}, status=405)


def predict_power_usage(request):
    past_data = EnergyUsage.objects.order_by('timestamp').values_list('timestamp', 'power1')[:100]
    
    # X: time as number, y: power
    X = np.array([(ts - past_data[0][0]).total_seconds() for ts, _ in past_data]).reshape(-1, 1)
    y = np.array([power for _, power in past_data])

    model = LinearRegression().fit(X, y)

    future_times = [past_data[-1][0] + timedelta(hours=i) for i in range(1, 13)]
    X_future = np.array([(ft - past_data[0][0]).total_seconds() for ft in future_times]).reshape(-1, 1)
    y_pred = model.predict(X_future)

    return JsonResponse({
        'labels': [dt.strftime('%H:%M') for dt in future_times],
        'predicted_power1': list(y_pred)
    })


@login_required
def change_profile(request):
    if request.method == "POST":
        user = request.user
        profile = user.profile

        print("📥 POST received")
        print("📁 FILES:", request.FILES)

        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")
        profile.phone = request.POST.get("phone")
        profile.address = request.POST.get("address")

        # 🧠 Critical part
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
            print(f"✅ Uploaded file: {profile.profile_picture}")
        else:
            print("❌ No profile picture uploaded")

        user.save()
        profile.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('user_dashboard')

def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()

@csrf_exempt
def record_energy_data(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        RealTimeEnergyData.objects.create(
            user=request.user,
            power_kw=data['power_kw']
        )
        return JsonResponse({'status': 'ok'})


@login_required
def monthly_power_data(request):
    """Returns average power per month."""
    data = (
        PowerReading.objects
        .filter(user=request.user)
        .annotate(month=TruncMonth('timestamp'))
        .values('month')
        .annotate(avg_power1=Avg('power1'), avg_power2=Avg('power2'))
        .order_by('month')
    )

    labels = [entry['month'].strftime('%b %Y') for entry in data]
    power1 = [round(entry['avg_power1'] or 0, 2) for entry in data]
    power2 = [round(entry['avg_power2'] or 0, 2) for entry in data]

    return JsonResponse({'labels': labels, 'power1': power1, 'power2': power2})

def report_data(request):
    user = request.user
    start_str = request.GET.get("start")
    end_str = request.GET.get("end")

    if not start_str or not end_str:
        return JsonResponse({"error": "Start and end dates are required."}, status=400)

    try:
        start = make_aware(datetime.strptime(start_str, "%Y-%m-%d"))
        end = make_aware(datetime.strptime(end_str, "%Y-%m-%d"))
    except ValueError:
        return JsonResponse({"error": "Invalid date format."}, status=400)

    qs = PowerReading.objects.filter(user=user, timestamp__range=(start, end))

    data = (
        qs.annotate(day=TruncDay("timestamp"))
        .values("day")
        .annotate(
            total_power1=Sum("power1"),
            total_power2=Sum("power2")
        )
        .order_by("day")
    )

    return JsonResponse(list(data), safe=False)

def report_csv(request):
    user = request.user
    start_str = request.GET.get("start")
    end_str = request.GET.get("end")

    start = make_aware(datetime.strptime(start_str, "%Y-%m-%d"))
    end = make_aware(datetime.strptime(end_str, "%Y-%m-%d"))

    qs = PowerReading.objects.filter(user=user, timestamp__range=(start, end))

    data = (
        qs.annotate(day=TruncDay("timestamp"))
        .values("day")
        .annotate(
            total_power1=Sum("power1"),
            total_power2=Sum("power2")
        )
        .order_by("day")
    )

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="power_report.csv"'

    writer = csv.writer(response)
    writer.writerow(["Date", "Power 1 (kWh)", "Power 2 (kWh)"])

    for entry in data:
        writer.writerow([
            entry["day"].strftime("%Y-%m-%d"),
            round(entry["total_power1"] or 0, 2),
            round(entry["total_power2"] or 0, 2)
        ])

    return response

def report_pdf(request):
    user = request.user
    start = request.GET.get("start")
    end = request.GET.get("end")

    start_date = make_aware(datetime.strptime(start, "%Y-%m-%d"))
    end_date = make_aware(datetime.strptime(end, "%Y-%m-%d"))

    qs = PowerReading.objects.filter(user=user, timestamp__range=(start_date, end_date))
    data = (
        qs.annotate(day=TruncDay("timestamp"))
        .values("day")
        .annotate(power1=Sum("power1"), power2=Sum("power2"))
        .order_by("day")
    )

    # ✅ Fix: These lines must be indented to be inside the function
    total_power1 = sum((entry["power1"] or 0) for entry in data)
    total_power2 = sum((entry["power2"] or 0) for entry in data)

    context = {
        "user": user,
        "start": start_date.date(),
        "end": end_date.date(),
        "rows": list(data),
        "timezone": get_current_timezone_name(),
        "total_power1": round(total_power1, 2),
        "total_power2": round(total_power2, 2),
        "request": request
    }

    template = get_template("report_pdf.html")
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="power_report.pdf"'

    # Use BytesIO instead of StringIO
    pisa.CreatePDF(io.BytesIO(html.encode("utf-8")), dest=response)

    return response
 
def save_live_reading(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = User.objects.get(username=data["username"])
            PowerReading.objects.create(
                user=user,
                power1=data["power1"],
                power2=data["power2"],
                battery_voltage=data.get("battery_voltage", 0)
            )
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)


@login_required
def grouped_power_data(request):
    range_type = request.GET.get("range", "day")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    data = get_grouped_power_data(
        user=request.user,
        range_type=range_type,
        start_date=start_date,
        end_date=end_date
    )
    return JsonResponse(data)



    def agg_between(start, end):
        qs = PowerReading.objects.filter(user=user, timestamp__gte=start, timestamp__lt=end)
        return (
            qs.aggregate(total=Sum('power1'))['total'] or 0,
            qs.aggregate(total=Sum('power2'))['total'] or 0
        )

    if start_date:
        delta = end_date - start_date

        if range_type in ("minute", "minutely"):
            step = timedelta(minutes=1)
            fmt = "%H:%M"
        elif range_type in ("hour", "hourly"):
            step = timedelta(hours=1)
            fmt = "%d %b %H:00"
        elif range_type in ("week", "weekly"):
            step = timedelta(days=1)
            fmt = "%a"
        elif range_type in ("month", "monthly"):
            step = timedelta(days=30)
            fmt = "%b %Y"
        else:
            return JsonResponse({"error": "Invalid range"}, status=400)

        current = start_date
        while current < end_date:
            next_step = current + step
            label = current.strftime(fmt)
            p1, p2 = agg_between(current, next_step)
            labels.append(label)
            power1.append(round(p1, 2))
            power2.append(round(p2, 2))
            current = next_step

    else:
        # Fall back to default pre-defined ranges
        if range_type in ("minute", "minutely"):
            for i in range(60):
                start = now - timedelta(minutes=60 - i)
                end = start + timedelta(minutes=1)
                labels.append(start.strftime("%H:%M"))
                p1, p2 = agg_between(start, end)
                power1.append(round(p1, 2))
                power2.append(round(p2, 2))
        elif range_type in ("hour", "hourly"):
            for i in range(24):
                start = now - timedelta(hours=24 - i)
                end = start + timedelta(hours=1)
                labels.append(start.strftime("%H:00"))
                p1, p2 = agg_between(start, end)
                power1.append(round(p1, 2))
                power2.append(round(p2, 2))
        elif range_type in ("week", "weekly"):
            for i in range(7):
                start = now - timedelta(days=7 - i)
                end = start + timedelta(days=1)
                labels.append(start.strftime("%a"))
                p1, p2 = agg_between(start, end)
                power1.append(round(p1, 2))
                power2.append(round(p2, 2))
        elif range_type in ("month", "monthly"):
            for i in range(12):
                start = now - timedelta(days=30 * (12 - i))
                end = start + timedelta(days=30)
                labels.append(start.strftime("%b"))
                p1, p2 = agg_between(start, end)
                power1.append(round(p1, 2))
                power2.append(round(p2, 2))
        else:
            return JsonResponse({"error": "Invalid range"}, status=400)

    return JsonResponse({
        "labels": labels,
        "power1": power1,
        "power2": power2,
        "power1_minutes": [],
        "power2_minutes": [],
        "power1_seconds": [],
        "power2_seconds": [],
    })

@csrf_exempt
def ingest_power_reading(request):
    """
    A simple HTTP endpoint your ESP can POST JSON to:
    {
      "power1": 123.4,
      "power2": 56.7,
      "voltage1": 230.1,
      ...
    }
    """
    if request.method != 'POST':
        return JsonResponse({"error": "POST only"}, status=405)

    data = json.loads(request.body)
    reading = PowerReading.objects.create(
        user = request.user if request.user.is_authenticated else None,
        power1 = data.get("power1", 0),
        power2 = data.get("power2", 0),
        voltage1 = data.get("voltage1", 0),
        voltage2 = data.get("voltage2", 0),
        current1 = data.get("current1", 0),
        current2 = data.get("current2", 0),
        energy1 = data.get("energy1", 0),
        energy2 = data.get("energy2", 0),
        frequency1 = data.get("frequency1", 0),
        frequency2 = data.get("frequency2", 0),
        power_factor1 = data.get("pf1", 0),
        power_factor2 = data.get("pf2", 0),
        battery_voltage = data.get("battery", 0),
        battery_percentage = data.get("battery_percentage", 0),
    )
    return JsonResponse({"status": "ok", "id": reading.id})

@csrf_exempt
def receive_energy_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')  # ESP should send username

            user = User.objects.get(username=username)

            energy_1 = float(data.get('energy_1', 0))
            energy_2 = float(data.get('energy_2', 0))
            total_energy = energy_1 + energy_2

            RealTimeEnergyData.objects.create(
                user=user,
                energy_1=energy_1,
                energy_2=energy_2,
                total_energy=total_energy
            )

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'detail': 'Method not allowed'}, status=405)

@login_required
def last_data_timestamp(request):
    latest = (
        PowerReading.objects.filter(user=request.user)
        .order_by("-timestamp")
        .values_list("timestamp", flat=True)
        .first()
    )

    if latest:
        return JsonResponse({"last_timestamp": latest.isoformat()})
    return JsonResponse({"last_timestamp": None})

@login_required
def power_summary_timestamps(request):
    user = request.user
    now = localtime()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())  # Monday
    month_start = today_start.replace(day=1)

    def latest_ts(qs):
        return qs.order_by("-timestamp").values_list("timestamp", flat=True).first()

    today_ts = latest_ts(PowerReading.objects.filter(user=user, timestamp__gte=today_start))
    week_ts = latest_ts(PowerReading.objects.filter(user=user, timestamp__gte=week_start))
    month_ts = latest_ts(PowerReading.objects.filter(user=user, timestamp__gte=month_start))

    return JsonResponse({
        "today": today_ts.isoformat() if today_ts else None,
        "week": (week_ts or today_ts).isoformat() if (week_ts or today_ts) else None,
        "month": (month_ts or today_ts).isoformat() if (month_ts or today_ts) else None,
    })

@never_cache
@login_required(login_url='/login/')
def admin_dashboard(request):
    today = now().date()

    # === Recent and counts ===
    recent_users = User.objects.filter(is_superuser=False).order_by('-date_joined')[:5]
    total_users = User.objects.filter(is_superuser=False).count()

    pending_work = PendingWork.objects.filter(is_completed=False).order_by('due_date')
    completed_work = PendingWork.objects.filter(is_completed=True).order_by('-due_date')[:5]
    total_pending_work = pending_work.count()
    total_contacts = Contact.objects.count()

    all_users = User.objects.filter(is_superuser=False).order_by('username')

    # === Chart Data Preparation ===

    # 📈 User Signups (Last 7 Days)
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    user_chart_labels = [day.strftime('%b %d') for day in last_7_days]
    user_chart_data = [
        User.objects.filter(date_joined__date=day, is_superuser=False).count()
        for day in last_7_days
    ]

    # 🛠 Tasks Completed (This Month)
    last_30_days = [today - timedelta(days=i) for i in range(29, -1, -1)]
    tasks_chart_labels = [day.strftime('%d') for day in last_30_days]
    tasks_chart_data = [
        PendingWork.objects.filter(is_completed=True, completed_at__date=day).count()
        for day in last_30_days
    ]

    # 📩 Contact Submissions (Last 7 Days)
    contact_chart_labels = user_chart_labels
    contact_chart_data = [
        Contact.objects.filter(created_at__date=day).count()
        for day in last_7_days
    ]

    context = {
        'recent_users': recent_users,
        'total_users': total_users,
        'pending_work': pending_work,
        'completed_work': completed_work,
        'total_pending_work': total_pending_work,
        'total_contacts': total_contacts,
        'all_users': all_users,

        # 🧠 Chart Data
        'user_chart_labels': user_chart_labels,
        'user_chart_data': user_chart_data,
        'tasks_chart_labels': tasks_chart_labels,
        'tasks_chart_data': tasks_chart_data,
        'contact_chart_labels': contact_chart_labels,
        'contact_chart_data': contact_chart_data,
    }

    return render(request, 'admin_dashboard.html', context)
@never_cache
@login_required(login_url='/login/')
def contact_submissions_page(request):
    recent_contacts = Contact.objects.order_by('-created_at')[:10]  # Fetch recent 10 submissions
    context = {
        'recent_contacts': recent_contacts,
    }
    return render(request, 'contact_submissions.html', context)

def reply_to_contact(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)

    if request.method == 'POST':
        # Get the reply from the form
        reply = request.POST.get('reply')

        # Save the reply to the contact
        contact.reply = reply
        contact.save()

        try:
            # Try to find the user by email
            user = User.objects.get(email=contact.email)
        except User.DoesNotExist:
            # If no user is found, create a new user (optional)
            user = User.objects.create_user(username=contact.email, email=contact.email, password='defaultpassword')

        # Create a notification for the user
        Notification.objects.create(
            user=user,
            message=f"You have received a reply to your contact submission: {contact.message[:50]}..."
        )

        # Redirect to the contact submissions page
        return redirect('contact_submissions_page')

    return redirect('contact_submissions_page') # fallback redirect

def send_notification(request):
    if request.method == 'POST':
        user_id = request.POST.get('user')
        message = request.POST.get('message')
        tag = request.POST.get('tag', 'info')

        if not message:
            return JsonResponse({'success': False, 'error': 'Message is required.'})

        try:
            if user_id:  # Single user
                user = User.objects.get(id=user_id)
                Notification.objects.create(user=user, message=message, tag=tag)
            else:  # Broadcast to all
                for user in User.objects.all():
                    Notification.objects.create(user=user, message=message, tag=tag)

            return JsonResponse({'success': True})
        except Exception as e:
            print(f"[send_notification ERROR]: {e}")
            return JsonResponse({'success': False, 'error': 'Internal error occurred.'})

    return JsonResponse({'success': False, 'error': 'Invalid request.'})

def check_new_notifications(request):
    user = request.user
    latest_unread = Notification.objects.filter(user=user, is_read=False).order_by('-created_at').first()

    if latest_unread:
        return JsonResponse({
            'has_new': True,
            'message': latest_unread.message
        })
    else:
        return JsonResponse({
            'has_new': False
        })

def notification_contact(request):
    contact_notifications = ContactNotification.objects.all()  # Example model
    return render(request, 'user_dashboard.html', {'contact_notifications': contact_notifications})

def create_notification(user, message):
    notification = Notification.objects.create(user=user, message=message)
    notification.save()

@login_required
def mark_notification_read(request, notif_id):
    try:
        notif = request.user.notifications.get(id=notif_id)
        notif.is_read = True
        notif.save()
        return JsonResponse({'success': True})
    except:
        return JsonResponse({'success': False})


def notifications_view(request):
    # Get all unread notifications for the current user
    notifications = Notification.objects.filter(user=request.user, read=False).order_by('-created_at')

    return render(request, 'notifications.html', {'notifications': notifications})

@login_required
def delete_notification(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.delete()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False}, status=404)


def mark_work_complete(request, work_id):
    work = get_object_or_404(PendingWork, id=work_id)
    work.is_completed = True
    work.save()
    return redirect('pending_work_list')

@never_cache
@login_required(login_url='/login/')
def pending_work_list(request):
    pending_work = PendingWork.objects.filter(is_completed=False, is_deleted=False).order_by('due_date')
    completed_work = PendingWork.objects.filter(is_completed=True, is_deleted=False).order_by('-due_date')

    context = {
        'pending_work': pending_work,
        'completed_work': completed_work,
    }
    return render(request, 'pending_work_list.html', context)

def delete_work(request, work_id):
    work = get_object_or_404(PendingWork, id=work_id)
    work.delete()
    return redirect('pending_work_list')

def delete_completed_work(request, work_id):
    work = get_object_or_404(PendingWork, id=work_id, is_completed=True, is_deleted=False)
    work.is_deleted = True
    work.deleted_at = now()
    work.save()
    return redirect('pending_work_list')

def restore_completed_work(request, work_id):
    work = get_object_or_404(PendingWork, id=work_id, is_completed=True)
    work.is_completed = False  # Mark as not completed
    work.save()
    return redirect('pending_work_list')

@never_cache
@login_required(login_url='/login/')
def add_pending_work(request):
    if request.method == 'POST':
        form = PendingWorkForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pending_work_list')  # Redirect to pending work list after saving
    else:
        form = PendingWorkForm()
    return render(request, 'add_pending_work.html', {'form': form})

def admin_logout(request):
    logout(request)
    return redirect('home') 

@login_required
def site_statistics(request):
    # Calculate durations manually for each session that has ended
    sessions = Session.objects.exclude(end_time=None)
    total_duration = sum((session.end_time - session.start_time).total_seconds() for session in sessions)
    avg_duration = total_duration / sessions.count() if sessions.exists() else "N/A"

    # Collecting site statistics data
    stats = {
        'user_count': User.objects.count(),
        'active_user_count': User.objects.filter(is_active=True).count(),
        'new_user_count': User.objects.filter(date_joined__gte=timezone.now() - timezone.timedelta(days=7)).count(),
        'page_views': PageView.objects.count(),
        'session_count': Session.objects.count(),
        'popular_content': Post.objects.order_by('-views').first().title if Post.objects.exists() else "N/A",
        'total_posts': Post.objects.count(),
        'total_comments': Comment.objects.count(),
        'avg_session_duration': avg_duration
    }

    return render(request, 'site_statistics.html', {'stats': stats})
@never_cache
@login_required(login_url='/login/')
def user_management(request):
    users = User.objects.select_related('profile').all()  # Optimize query to include profile data
    context = {
        'users': users,
    }
    return render(request, 'user_management.html', context)

@never_cache
@login_required(login_url='/login/')
def add_user(request):
    if request.method == 'POST':
        form = ClientCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New client created successfully.")
            return redirect('user_management')
        else:
            messages.error(request, "There was an error creating the client. Please check the form.")
    else:
        form = ClientCreationForm()
    return render(request, 'add_user.html', {'form': form})

@login_required
def edit_user(request, user_id):
    if request.method == 'POST':
        try:
            user = User.objects.get(pk=user_id)
            user.username = request.POST.get('username')
            user.email = request.POST.get('email')
            role = request.POST.get('role')

            # Set role
            user.is_superuser = True if role == 'superuser' else False
            user.is_staff = True if role in ['admin', 'superuser'] else False

            user.save()

            return JsonResponse({'success': True})
        except Exception as e:
            print(f"Error updating user: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@never_cache
@login_required(login_url='/login/')
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('user_management')
    
    return render(request, 'delete_user.html', {'user': user})

@never_cache
@login_required(login_url='/login/')
def website_configuration(request):
    # Get or create the website configuration instance
    config, created = WebsiteConfiguration.objects.get_or_create(
        id=1,
        defaults={
            'site_name': "5RS Construction Services",
            'contact_email': "fiversconstruction@yahoo.com",
            'contact_phone': "09089074031",
            'address': "Bayanan, Bacoor Cavite",
            'facebook_page': "https://www.facebook.com/5rsconstruction",
            'footer_text': "Copyright © 2024 All Rights Reserved.",
        }
    )

    if request.method == 'POST':
        # Update general fields
        config.site_name = request.POST.get('site_name', config.site_name)
        config.contact_email = request.POST.get('contact_email', config.contact_email)
        config.contact_phone = request.POST.get('contact_phone', config.contact_phone)
        config.address = request.POST.get('address', config.address)
        config.facebook_page = request.POST.get('facebook_page', config.facebook_page)
        config.footer_text = request.POST.get('footer_text', config.footer_text)

        # Update About Us section
        config.about_us_text_1 = request.POST.get('about_us_text_1', config.about_us_text_1)
        config.about_us_text_2 = request.POST.get('about_us_text_2', config.about_us_text_2)
        config.about_us_text_3 = request.POST.get('about_us_text_3', config.about_us_text_3)
        if 'about_us_image' in request.FILES:
            config.about_us_image = request.FILES['about_us_image']

        # Update Portfolio section with multiple images and texts
        if 'portfolio_image_1' in request.FILES:
            config.portfolio_image_1 = request.FILES['portfolio_image_1']
        config.portfolio_text_1 = request.POST.get('portfolio_text_1', config.portfolio_text_1)
        config.portfolio_text_2 = request.POST.get('portfolio_text_2', config.portfolio_text_2)

        if 'portfolio_image_2' in request.FILES:
            config.portfolio_image_2 = request.FILES['portfolio_image_2']
        config.portfolio_text_3 = request.POST.get('portfolio_text_3', config.portfolio_text_3)
        config.portfolio_text_4 = request.POST.get('portfolio_text_4', config.portfolio_text_4)

        if 'portfolio_image_3' in request.FILES:
            config.portfolio_image_3 = request.FILES['portfolio_image_3']
        config.portfolio_text_5 = request.POST.get('portfolio_text_5', config.portfolio_text_5)
        config.portfolio_text_6 = request.POST.get('portfolio_text_6', config.portfolio_text_6)

        if 'portfolio_image_4' in request.FILES:
            config.portfolio_image_4 = request.FILES['portfolio_image_4']
        config.portfolio_text_7 = request.POST.get('portfolio_text_7', config.portfolio_text_7)
        config.portfolio_text_8 = request.POST.get('portfolio_text_8', config.portfolio_text_8)

        if 'portfolio_image_5' in request.FILES:
            config.portfolio_image_5 = request.FILES['portfolio_image_5']
        config.portfolio_text_9 = request.POST.get('portfolio_text_9', config.portfolio_text_9)
        config.portfolio_text_10 = request.POST.get('portfolio_text_10', config.portfolio_text_10)

        if 'portfolio_image_6' in request.FILES:
            config.portfolio_image_6 = request.FILES['portfolio_image_6']
        config.portfolio_text_11 = request.POST.get('portfolio_text_11', config.portfolio_text_11)
        config.portfolio_text_12 = request.POST.get('portfolio_text_12', config.portfolio_text_12)

        config.save()

        messages.success(request, "Website configuration updated successfully.")
        return redirect('website_configuration')

    return render(request, 'website_configuration.html', {'config': config})

def some_view(request):
    messages.success(request, "Your profile has been updated successfully.")


@never_cache
@login_required(login_url='/login/')
def update_account(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        password_form = UpdatePasswordForm(user=request.user, data=request.POST)
        
        # Check if both forms are valid
        if user_form.is_valid() and password_form.is_valid():
            # Save the changes to user and password
            user_form.save()
            password_form.save()
            update_session_auth_hash(request, password_form.user)  # Prevents logout after password change
            
            # Success message
            messages.success(request, 'Your account has been updated successfully!')
            return redirect('user_dashboard')
        else:
            # Error message if forms are invalid
            if not user_form.is_valid():
                messages.error(request, 'Failed to update account details. Please check the form for errors.')
            if not password_form.is_valid():
                messages.error(request, 'Failed to update password. Please check the form for errors.')
    else:
        # Load the forms for GET request
        user_form = UpdateUserForm(instance=request.user)
        password_form = UpdatePasswordForm(user=request.user)

    context = {
        'user_form': user_form,
        'password_form': password_form,
    }
    return render(request, 'update_account.html', context)

@never_cache
@login_required(login_url='/login/')
def user_faq(request):
    faqs = [
        {
            "question": "How can I reset my password?",
            "answer": "You can reset your password by going to 'Update Account' and using the password section."
        },
        {
            "question": "How do I monitor my power usage?",
            "answer": "Navigate to 'Energy Monitoring' to view live charts and historical data."
        },
        {
            "question": "What is live power chart?",
            "answer": "It’s a real-time graph that updates automatically with your device power usage."
        },
        {
            "question": "Can I update my email address?",
            "answer": "Yes. Go to 'Update Account', and update your email directly from the form."
        }
    ]
    return render(request, "user_faq.html", {"faqs": faqs})

@never_cache
@login_required(login_url='/login/')
def energy_monitoring(request):
    # Replace this with how you're actually gathering the last 30 seconds/minutes of data
    recent_data = RealTimeEnergyData.objects.filter(user=request.user).order_by('-timestamp')[:30][::-1]

    # Build the data lists
    time_labels = [entry.timestamp.strftime('%H:%M:%S') for entry in recent_data]
    voltage1_list = [entry.voltage_1 for entry in recent_data]
    voltage2_list = [entry.voltage_2 for entry in recent_data]
    power1_list = [entry.power_1 for entry in recent_data]  # ✅ assuming your model has this field
    power2_list = [entry.power_2 for entry in recent_data]  # ✅ assuming your model has this field

    context = {
    'times_in_seconds': json.dumps(time_labels),  # x-axis
    'power1_values': json.dumps(power1_list),     # y-axis: Power 1
    'power2_values': json.dumps(power2_list),     # y-axis: Power 2
}

    return render(request, 'energy_monitoring.html', context)

@csrf_exempt
def save_voltage_reading(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        voltage_1 = float(data['voltage1'])
        voltage_2 = float(data['voltage2'])

        RealTimeEnergyData.objects.create(
            user=request.user,
            voltage_1=voltage_1,
            voltage_2=voltage_2,
        )
        return JsonResponse({'status': 'saved'})

@csrf_exempt
def save_realtime_data(request):
    if request.method == "POST":
        data = json.loads(request.body)
        voltage1 = float(data.get("voltage1", 0))
        voltage2 = float(data.get("voltage2", 0))
        battery = float(data.get("battery", 0))

        RealTimeEnergyData.objects.create(
            user=request.user,
            voltage_1=voltage1,
            voltage_2=voltage2,
            battery_percentage=battery
        )
        return JsonResponse({"status": "ok"})


def check_energy_spike(user):
    # Calculate energy usage for the last 7 days
    last_week = now() - timedelta(days=7)
    recent_energy_data = EnergyUsage.objects.filter(user=user, date__gte=last_week)

    # Check if there is any recent energy data
    if not recent_energy_data:
        return  # Exit the function if there is no data to prevent division by zero

    # Define threshold for a spike (e.g., 20% higher than average)
    threshold_multiplier = 1.2
    avg_usage = sum([data.energy_consumed for data in recent_energy_data]) / len(recent_energy_data)

    # Check if the latest usage exceeds the threshold
    if recent_energy_data.latest('date').energy_consumed > avg_usage * threshold_multiplier:
        # If there is a spike, create a notification
        Notification.objects.create(
            user=user,
            type="alert",
            content="Your energy usage has spiked. Consider reviewing your consumption."
        )

def check_profile_completion(user):
    if not user.first_name or not user.email:
        # Create a notification if essential fields are missing
        Notification.objects.create(
            user=user,
            type="info",
            content="Please complete your profile information to improve your experience."
        )

def delete_contact_permanent(request, contact_id):
    if request.method == 'POST':  # Ensure it's a POST request
        contact = get_object_or_404(Contact, id=contact_id)
        contact.delete()  # Permanently delete the contact
        messages.success(request, 'The contact submission has been permanently deleted.')
    return redirect('archived_contacts')  # Redirect back to the archived contacts page

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Prevent logout
            messages.success(request, 'Your password was successfully updated!')
        else:
            messages.error(request, 'Please correct the error below.')
    return redirect('admin_dashboard')  # Or wherever you want to return

def export_users_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Username', 'Email', 'Role', 'Status', 'Join Date'])

    for user in User.objects.all():
        writer.writerow([
            user.id, user.username, user.email,
            'Super Admin' if user.is_superuser else 'Admin' if user.is_staff else 'User',
            'Active' if user.is_active else 'Inactive',
            user.date_joined.strftime('%Y-%m-%d')
        ])

    return response