from django.contrib import admin
from django.http import HttpResponse
from django.core.mail import send_mass_mail
from django.conf import settings
from django.utils import timezone
import csv
import io


def export_as_csv(modeladmin, request, queryset):
    """Export selected objects as CSV"""
    meta = modeladmin.model._meta
    field_names = [field.name for field in meta.fields]
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={meta}.csv'
    
    writer = csv.writer(response)
    writer.writerow(field_names)
    
    for obj in queryset:
        row = []
        for field in field_names:
            value = getattr(obj, field)
            if callable(value):
                try:
                    value = value() or ''
                except:
                    value = 'Error retrieving value'
            if value is None:
                value = ''
            row.append(str(value))
        writer.writerow(row)
    
    return response

export_as_csv.short_description = "Export selected items as CSV"


def send_email_notification(modeladmin, request, queryset):
    """Send email notifications to selected users"""
    if not hasattr(queryset.first(), 'email'):
        modeladmin.message_user(request, "Selected objects don't have email field", level='ERROR')
        return
    
    emails = []
    subject = f"Notification from {settings.SITE_NAME if hasattr(settings, 'SITE_NAME') else 'Access Auto Services'}"
    message = "This is a notification from our admin panel."
    from_email = settings.DEFAULT_FROM_EMAIL
    
    for obj in queryset:
        if hasattr(obj, 'email') and obj.email:
            emails.append((subject, message, from_email, [obj.email]))
    
    if emails:
        try:
            send_mass_mail(emails, fail_silently=False)
            modeladmin.message_user(request, f"Successfully sent {len(emails)} email notifications.")
        except Exception as e:
            modeladmin.message_user(request, f"Error sending emails: {str(e)}", level='ERROR')
    else:
        modeladmin.message_user(request, "No valid email addresses found.", level='WARNING')

send_email_notification.short_description = "Send email notification to selected users"


def mark_as_active(modeladmin, request, queryset):
    """Mark selected objects as active"""
    if hasattr(queryset.first(), 'is_active'):
        updated = queryset.update(is_active=True)
        modeladmin.message_user(request, f"{updated} items marked as active.")
    elif hasattr(queryset.first(), 'active'):
        updated = queryset.update(active=True)
        modeladmin.message_user(request, f"{updated} items marked as active.")
    else:
        modeladmin.message_user(request, "Selected objects don't have active field", level='ERROR')

mark_as_active.short_description = "Mark selected items as active"


def mark_as_inactive(modeladmin, request, queryset):
    """Mark selected objects as inactive"""
    if hasattr(queryset.first(), 'is_active'):
        updated = queryset.update(is_active=False)
        modeladmin.message_user(request, f"{updated} items marked as inactive.")
    elif hasattr(queryset.first(), 'active'):
        updated = queryset.update(active=False)
        modeladmin.message_user(request, f"{updated} items marked as inactive.")
    else:
        modeladmin.message_user(request, "Selected objects don't have active field", level='ERROR')

mark_as_inactive.short_description = "Mark selected items as inactive"


def duplicate_objects(modeladmin, request, queryset):
    """Duplicate selected objects"""
    duplicated_count = 0
    
    for obj in queryset:
        # Get all field values
        field_values = {}
        for field in obj._meta.fields:
            if field.name != obj._meta.pk.name:  # Skip primary key
                field_values[field.name] = getattr(obj, field.name)
        
        # Create new object
        try:
            new_obj = obj.__class__.objects.create(**field_values)
            duplicated_count += 1
        except Exception as e:
            modeladmin.message_user(
                request, 
                f"Error duplicating {obj}: {str(e)}", 
                level='ERROR'
            )
    
    if duplicated_count > 0:
        modeladmin.message_user(request, f"Successfully duplicated {duplicated_count} items.")

duplicate_objects.short_description = "Duplicate selected items"


def generate_summary_report(modeladmin, request, queryset):
    """Generate a summary report for selected objects"""
    model_name = modeladmin.model._meta.verbose_name_plural
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={model_name}_summary_report.csv'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([f'{model_name.title()} Summary Report'])
    writer.writerow([f'Generated on: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}'])
    writer.writerow([f'Total items: {queryset.count()}'])
    writer.writerow([])  # Empty row
    
    # Write field summary
    writer.writerow(['Field', 'Unique Values', 'Most Common Value'])
    
    for field in modeladmin.model._meta.fields:
        if field.name in ['id', 'password']:  # Skip sensitive fields
            continue
            
        try:
            values = queryset.values_list(field.name, flat=True)
            unique_values = set(values)
            
            if len(unique_values) <= 20:  # Only for fields with reasonable number of unique values
                from collections import Counter
                most_common = Counter(values).most_common(1)
                most_common_value = most_common[0][0] if most_common else 'N/A'
                
                writer.writerow([
                    field.verbose_name,
                    len(unique_values),
                    str(most_common_value)
                ])
        except:
            continue
    
    return response

generate_summary_report.short_description = "Generate summary report for selected items"


# Register actions globally
admin.site.add_action(export_as_csv)
admin.site.add_action(mark_as_active)
admin.site.add_action(mark_as_inactive)
admin.site.add_action(generate_summary_report)