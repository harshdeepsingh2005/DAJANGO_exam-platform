from django.contrib.auth.models import User

def create_dummy_users():
    # Admin users
    admins = [
        ('admin1', 'adminpass1'),
        ('admin2', 'adminpass2'),
        ('admin3', 'adminpass3'),
    ]
    for username, password in admins:
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, password=password, email=f'{username}@example.com')

    # Normal users
    users = [
        ('user1', 'userpass1'),
        ('user2', 'userpass2'),
        ('user3', 'userpass3'),
    ]
    for username, password in users:
        if not User.objects.filter(username=username).exists():
            User.objects.create_user(username=username, password=password, email=f'{username}@example.com')

if __name__ == '__main__':
    create_dummy_users()
    print('Dummy users created.')
