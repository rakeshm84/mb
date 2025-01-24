from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Tenant, UserProfile

from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.contrib.auth.password_validation import validate_password
from .validation_messages import ValidationMessages
from django.utils.translation import gettext_lazy as _
import re
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active']

    def __init__(self, *args, **kwargs):
            context = kwargs.get('context', {})
            bypass_userprofile = context.get('bypass_userprofile', False)
            if bypass_userprofile:
                self.fields.pop('profile', None)
            super().__init__(*args, **kwargs)
    
    def to_internal_value(self, data):
        errors = {}
        
        # Validate username
        username = data.get('username', '').strip()
        if not username:
            errors.setdefault('username', []).append(ValidationMessages.USERNAME_REQUIRED)
        elif User.objects.filter(username=username).exists():
            errors.setdefault('username', []).append(ValidationMessages.USERNAME_NOT_UNIQUE)
        elif ' ' in username:
            errors.setdefault('username', []).append(ValidationMessages.USERNAME_NO_SPACES)

        # Validate email
        email = data.get('email', '').strip()
        if not email:
            errors.setdefault('email', []).append(ValidationMessages.EMAIL_REQUIRED)
        else:
            email_validator = EmailValidator()
            try:
                email_validator(email)
            except ValidationError:
                errors.setdefault('email', []).append(ValidationMessages.EMAIL_INVALID)
            if User.objects.filter(email=email).exists():
                errors.setdefault('email', []).append(ValidationMessages.EMAIL_NOT_UNIQUE)

        # Validate password
        password = data.get('password', '').strip()
        if not password:
            errors.setdefault('password', []).append(ValidationMessages.PASSWORD_REQUIRED)
        else:
            if not re.search(r'[A-Z]', password):
                errors.setdefault('password', []).append(ValidationMessages.PASSWORD_UPPERCASE)
            if not re.search(r'[a-z]', password):
                errors.setdefault('password', []).append(ValidationMessages.PASSWORD_LOWERCASE)
            if not re.search(r'\d', password):
                errors.setdefault('password', []).append(ValidationMessages.PASSWORD_DIGIT)
            if not re.search(r'[@$!%*?&\-_+=.,#^~:;|/\\]', password):
                errors.setdefault('password', []).append(ValidationMessages.PASSWORD_SPECIAL_CHAR)

        # Validate first_name
        first_name = data.get('first_name', '').strip()
        if not first_name:
            errors.setdefault('first_name', []).append(ValidationMessages.FIRST_NAME_REQUIRED)
        elif not first_name.isalpha():
            errors.setdefault('first_name', []).append(ValidationMessages.FIRST_NAME_NOT_VALID)

        # Validate last_name
        last_name = data.get('last_name', '').strip()
        if not last_name:
            errors.setdefault('last_name', []).append(ValidationMessages.LAST_NAME_REQUIRED)
        elif not last_name.isalpha():
            errors.setdefault('last_name', []).append(ValidationMessages.LAST_NAME_NOT_VALID)

        # Raise errors if any
        if errors:
            raise serializers.ValidationError(errors)

        return super().to_internal_value(data)

    def create(self, validated_data):
        # Create a new user with a hashed password
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        
        UserProfile.objects.create(
            user=user, 
            phone_number=validated_data.get('phone_number', None),
            address=validated_data.get('address', None),
            date_of_birth=validated_data.get('dob', None),
            language='en',
        )

        return user

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = '__all__'

    def to_representation(self, instance):
        # Call the default serialization
        data = super().to_representation(instance)
        
        # Add user_data dynamically if it exists
        if hasattr(instance, 'user_data'):
            data['user_data'] = instance.user_data
        
        return data
    
    def validate_subdomain(self, value):
      
        if not value:
            raise ValidationError(ValidationMessages.SUBDOMAIN_REQUIRED)
        value = value.strip().lower()  
        value = re.sub(r'[^a-z0-9-]', '-', value)
        value = re.sub(r'-{2,}', '-', value)
        value = value.strip('-')

        if Tenant.objects.filter(subdomain=value).exists():
            raise ValidationError(ValidationMessages.SUBDOMAIN_EXISTS)
       
        return value

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod

    def get_token(cls, user):
        token = super().get_token(user)
        tenant_id = 0
        if hasattr(user, 'profile'):
            tenant_id = user.profile.tenant_id

        token['username'] = user.username
        token['email'] = user.email
        token['is_superuser'] = user.is_superuser
        token['parent_tenant_id'] = tenant_id
        token['is_tenant'] = False

        if tenant_id:
            tenant_data = Tenant.objects.filter(id=tenant_id).first()
        else:
            tenant_data = Tenant.objects.filter(entity_id=user.id).first()
        if tenant_data:
            user_permissions = user.get_all_permissions(tenant_data.id)
            token['is_tenant'] = True
            token['tenant_id'] = tenant_data.id
            token['tenant_parent_id'] = tenant_data.parent_id
            token['db_name'] = tenant_data.db_name
            token['dsn'] = tenant_data.dsn
            token['entity_type'] = tenant_data.entity
            token['permissions'] = list(user_permissions)
        return token