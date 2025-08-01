from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create admin user with specific credentials'

    def handle(self, *args, **options):
        email = 'gotbae2@gmail.com'
        password = 'Gotbae804.__'
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            # Update existing user to be superuser
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Updated existing user {email} with admin privileges')
            )
        else:
            # Create new superuser
            user = User.objects.create_superuser(
                email=email,
                password=password,
                first_name='Admin',
                last_name='User'
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Created new superuser: {email}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🔐 Admin Credentials:\n'
                f'   Email: {email}\n'
                f'   Password: {password}\n'
                f'\n🌐 Access URLs:\n'
                f'   Admin Panel: http://127.0.0.1:8000/admin/\n'
                f'   Dashboard: http://127.0.0.1:8000/admin-dashboard/\n'
            )
        )