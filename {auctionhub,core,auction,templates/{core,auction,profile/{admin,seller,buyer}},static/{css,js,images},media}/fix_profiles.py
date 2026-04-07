"""
Run once to create missing profiles for any existing users (especially superusers).

  python manage.py shell < fix_profiles.py

"""
from django.contrib.auth.models import User
from core.models import UserProfile

fixed = 0
for user in User.objects.all():
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={'role': 'admin' if user.is_staff else 'buyer'}
    )
    if created:
        print(f"  Created profile for: {user.username}  (role={profile.role})")
        fixed += 1

if fixed == 0:
    print("  All users already have profiles — nothing to fix.")
else:
    print(f"\n  Done. Fixed {fixed} user(s).")