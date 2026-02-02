from django.contrib.auth.models import User

for user in User.objects.all():
    print(f"Username: {user.username}, is_superuser: {user.is_superuser}, email: {user.email}")
