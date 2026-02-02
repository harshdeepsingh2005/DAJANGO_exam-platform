#!/usr/bin/env python
import os
import django
import sys

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_platform.settings')
django.setup()

from django.contrib.auth.models import User

def create_and_verify_users():
    print("Creating dummy users...")
    
    # Admin users
    admin_users = [
        ('admin1', 'adminpass1'),
        ('admin2', 'adminpass2'), 
        ('admin3', 'adminpass3'),
    ]
    
    for username, password in admin_users:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@example.com',
                'is_superuser': True,
                'is_staff': True
            }
        )
        if created:
            user.set_password(password)
            user.save()
            print(f"Created admin user: {username}")
        else:
            # Update password in case it was wrong
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            print(f"Updated admin user: {username}")
    
    # Normal users
    normal_users = [
        ('user1', 'userpass1'),
        ('user2', 'userpass2'),
        ('user3', 'userpass3'),
    ]
    
    for username, password in normal_users:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@example.com',
                'is_superuser': False,
                'is_staff': False
            }
        )
        if created:
            user.set_password(password)
            user.save()
            print(f"Created normal user: {username}")
        else:
            # Update password in case it was wrong
            user.set_password(password)
            user.save()
            print(f"Updated normal user: {username}")
    
    print("\nVerifying all users:")
    for user in User.objects.all():
        print(f"- {user.username}: superuser={user.is_superuser}, staff={user.is_staff}, email={user.email}")

if __name__ == '__main__':
    create_and_verify_users()