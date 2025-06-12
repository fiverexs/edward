from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model 
from datetime import date
from django.conf import settings
from django.utils import timezone



class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    reply = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name} - {self.email}"
        
class PendingWork(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.is_completed and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)

    
class ArchivedContact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField()
    created_at = models.DateTimeField()  # Original creation date
    archived_at = models.DateTimeField(auto_now_add=True)  # Date archived

    def __str__(self):
        return f"Archived message from {self.name} - {self.email}"


class BannerImage(models.Model):
    image = models.ImageField(upload_to='banners/')

class Headline(models.Model):
    text = models.CharField(max_length=100)

class Paragraph(models.Model):
    text = models.TextField()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    
    
    def __str__(self):
        return self.user.username

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='profile_pictures/default.jpg')

    def __str__(self):
        return f"{self.user.username}'s Profile"


class PageView(models.Model):
    """Tracks each page view on the website."""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    page_url = models.URLField(max_length=200)
    timestamp = models.DateTimeField(default=timezone.now)
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.page_url} viewed on {self.timestamp}"


class Session(models.Model):
    """Tracks user sessions on the site."""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)

    @property
    def duration(self):
        """Calculate the duration of the session in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def __str__(self):
        duration_str = f"{self.duration // 60} min" if self.duration else "In Progress"
        return f"Session by {self.user} - {duration_str}"


class Post(models.Model):
    """Represents articles or content on the site."""
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Tracks comments on posts."""
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.user} on {self.post}"

class HomePageContent(models.Model):
    title = models.CharField(max_length=200, default="5RS CONSTRUCTION SERVICES")
    subtitle = models.TextField()
    button_text = models.CharField(max_length=50, default="Call us Now!")
    
    def __str__(self):
        return self.title


# Model for individual services
class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon_class = models.CharField(max_length=50, help_text="CSS class for the icon, e.g., 'bx bxs-coffee-bean'")
    link = models.URLField(blank=True, null=True, help_text="Optional URL for more info")
    
    def __str__(self):
        return self.name

# Model for portfolio projects
class PortfolioProject(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='portfolio/')
    
    def __str__(self):
        return self.title

class WebsiteConfiguration(models.Model):
    # Existing fields for general configuration
    site_name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    facebook_page = models.URLField(blank=True, null=True)
    footer_text = models.TextField(blank=True, null=True)

    # New fields for "About Us"
    about_us_text_1 = models.TextField(blank=True, null=True)
    about_us_text_2 = models.TextField(blank=True, null=True)
    about_us_text_3 = models.TextField(blank=True, null=True)
    about_us_image = models.ImageField(upload_to='about_us/', blank=True, null=True)

    # New fields for "Portfolio"
    portfolio_image_1 = models.ImageField(upload_to='portfolio/', blank=True, null=True)
    portfolio_text_1 = models.CharField(max_length=200, blank=True, null=True)
    portfolio_text_2 = models.TextField(blank=True, null=True)

    portfolio_image_2 = models.ImageField(upload_to='portfolio/', blank=True, null=True)
    portfolio_text_3 = models.CharField(max_length=200, blank=True, null=True)
    portfolio_text_4 = models.TextField(blank=True, null=True)

    portfolio_image_3 = models.ImageField(upload_to='portfolio/', blank=True, null=True)
    portfolio_text_5 = models.CharField(max_length=200, blank=True, null=True)
    portfolio_text_6 = models.TextField(blank=True, null=True)

    portfolio_image_4 = models.ImageField(upload_to='portfolio/', blank=True, null=True)
    portfolio_text_7 = models.CharField(max_length=200, blank=True, null=True)
    portfolio_text_8 = models.TextField(blank=True, null=True)

    portfolio_image_5 = models.ImageField(upload_to='portfolio/', blank=True, null=True)
    portfolio_text_9 = models.CharField(max_length=200, blank=True, null=True)
    portfolio_text_10 = models.TextField(blank=True, null=True)

    portfolio_image_6 = models.ImageField(upload_to='portfolio/', blank=True, null=True)
    portfolio_text_11 = models.CharField(max_length=200, blank=True, null=True)
    portfolio_text_12 = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.site_name

class EnergyUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    energy_consumed = models.DecimalField(max_digits=10, decimal_places=2)  # in kWh

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.energy_consumed} kWh"

class AdminMessage(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    TAG_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('alert', 'Alert'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    tag = models.CharField(max_length=20, choices=TAG_CHOICES, default='info')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"To: {self.user.username} | {self.message[:40]}"

    class Meta:
        ordering = ['-created_at']

class EnergySystem(models.Model):
    system_size_kwp = models.FloatField(default=0.0, verbose_name="System Size (kWp)")
    battery_charge_percentage = models.FloatField(default=0.0, verbose_name="Battery Charge (%)")
    battery_status = models.CharField(max_length=50, choices=[
        ('Charging', 'Charging'),
        ('Discharging', 'Discharging'),
        ('Idle', 'Idle')
    ], default='Idle', verbose_name="Battery Status")
    battery_health = models.CharField(max_length=50, default='Good', verbose_name="Battery Health")
    solar_production_kw = models.FloatField(default=0.0, verbose_name="Solar Production (kW)")

    def __str__(self):
        return f"Energy System Overview - {self.system_size_kwp} kWp"

    class Meta:
        verbose_name = "Energy System"
        verbose_name_plural = "Energy Systems"

class EnergyConsumption(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.CharField(max_length=20)  # e.g., "January", "February"
    year = models.IntegerField()
    consumption = models.FloatField()  # e.g., in kWh

    def __str__(self):
        return f"{self.user.username} - {self.month} {self.year}"

class RealTimeEnergyData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    energy_1 = models.FloatField()
    energy_2 = models.FloatField()
    total_energy = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} | {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

class PowerReading(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='power_readings')

    # Live sensor readings
    timestamp = models.DateTimeField(auto_now_add=True)
    power1 = models.FloatField(default=0.0, help_text="Power from source 1 (Watts)")
    power2 = models.FloatField(default=0.0, help_text="Power from source 2 (Watts)")

    voltage1 = models.FloatField(default=0.0, help_text="Voltage Line 1 (V)")
    voltage2 = models.FloatField(default=0.0, help_text="Voltage Line 2 (V)")

    current1 = models.FloatField(default=0.0, help_text="Current Line 1 (A)")
    current2 = models.FloatField(default=0.0, help_text="Current Line 2 (A)")

    energy1 = models.FloatField(default=0.0, help_text="Energy consumed on line 1 (kWh)")
    energy2 = models.FloatField(default=0.0, help_text="Energy consumed on line 2 (kWh)")

    frequency1 = models.FloatField(default=0.0, help_text="Frequency line 1 (Hz)")
    frequency2 = models.FloatField(default=0.0, help_text="Frequency line 2 (Hz)")

    power_factor1 = models.FloatField(default=0.0, help_text="Power Factor line 1")
    power_factor2 = models.FloatField(default=0.0, help_text="Power Factor line 2")

    battery_voltage = models.FloatField(default=0.0, help_text="Battery voltage (V)")
    battery_percentage = models.FloatField(default=0.0, help_text="Battery charge (%)")

    def __str__(self):
        return f"{self.user.username} @ {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        ordering = ['-timestamp']



