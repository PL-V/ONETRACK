from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # Create the user without passing the role directly
        user = self.create_user(username, email, password, **extra_fields)

        # Assign the Superuser role
        superuser_role = Role.objects.create(name='Superuser')
        user.roles.add(superuser_role)
        return user


class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    ROLE_CHOICES = [
        ('Reporter', 'Reporter'),
        ('Owner', 'Owner'),
        ('Remediator', 'Remediator'),
        ('Verifier', 'Verifier'),
        ('Superuser', 'Superuser'),
    ]
    name = models.CharField(max_length=20, choices=ROLE_CHOICES)
    class Meta:
        db_table = 'role'

    def __str__(self):
        return self.name
    @staticmethod
    def get_role_choices():
        return [(choice[0], choice[1]) for choice in Role.ROLE_CHOICES]
    

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255,null=True, blank=True)
    email = models.EmailField(unique=True)
    roles = models.ManyToManyField(Role, related_name='users', blank=True)
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    team = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'user'
