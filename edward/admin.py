from django.contrib import admin
from .models import Contact, HomePageContent, Service, PortfolioProject, WebsiteConfiguration, AdminMessage, EnergySystem, Notification, PowerReading
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.models import User

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email', 'phone')

@admin.register(HomePageContent)
class HomePageContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'button_text')  # Fields to display in the admin list view

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_class')
    search_fields = ('name',)  # Searchable by name in the admin

@admin.register(PortfolioProject)
class PortfolioProjectAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)

class WebsiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'contact_email', 'contact_phone')
    filter_horizontal = ('projects',)  # Allow selecting multiple projects

class AdminMessageAdmin(admin.ModelAdmin):
    list_display = ('content', 'created_at')

admin.site.register(AdminMessage, AdminMessageAdmin)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'tag', 'is_read', 'created_at']
    
    def save_model(self, request, obj, form, change):
        if obj.is_broadcast:
            # Create individual notification per user
            users = User.objects.all()
            Notification.objects.bulk_create([
                Notification(user=u, message=obj.message, link=obj.link) for u in users
            ])
        else:
            # Save normally for single user
            super().save_model(request, obj, form, change)


class EnergySystemAdmin(admin.ModelAdmin):
    list_display = ('system_size_kwp', 'battery_charge_percentage', 'battery_status', 'battery_health', 'solar_production_kw')
    list_editable = ('system_size_kwp', 'battery_charge_percentage', 'battery_status', 'battery_health', 'solar_production_kw')
    list_per_page = 10

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'image')
    search_fields = ('title', 'description')

@admin.register(PowerReading)
class PowerReadingAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'power1', 'power2')
    list_filter = ('user', 'timestamp')
    search_fields = ('user__username',)
