from django.utils.translation import gettext_lazy as _

class ValidationMessages:
    USERNAME_REQUIRED = 'lang.validations.username.required'
    USERNAME_NOT_UNIQUE = 'lang.validations.username.not_unique'
    USERNAME_ALREADY_CREATED = 'lang.validations.username.already_created'
    USERNAME_NOT_UNIQUE_CREATE_NEW_USER = 'lang.validations.username.not_unique_create_new_user'
    
    EMAIL_REQUIRED = 'lang.validations.email.required'
    EMAIL_INVALID = 'lang.validations.email.invalid'
    EMAIL_NOT_UNIQUE = 'lang.validations.email.not_unique'
    EMAIL_ALREADY_CREATED = 'lang.validations.email.already_created'
    EMAIL_NOT_UNIQUE_CREATE_NEW_USER = 'lang.validations.email.not_unique_create_new_user'

    PASSWORD_REQUIRED = 'lang.validations.password.required'
    PASSWORD_UPPERCASE = 'lang.validations.password.contains_uppercase'
    PASSWORD_LOWERCASE = 'lang.validations.password.contains_lowercase'
    PASSWORD_DIGIT = 'lang.validations.password.contains_digit'
    PASSWORD_SPECIAL_CHAR = 'lang.validations.password.contains_special_char'

    FIRST_NAME_REQUIRED = 'lang.validations.first_name_required'
    FIRST_NAME_NOT_VALID = 'lang.validations.first_name_not_valid'
    LAST_NAME_REQUIRED = 'lang.validations.last_name_required'
    LAST_NAME_NOT_VALID = 'lang.validations.last_name_not_valid'
    
    SUBDOMAIN_REQUIRED = 'lang.validations.required'
    SUBDOMAIN_EXISTS = 'lang.validations.subdomain_exists'
    SUBDOMAIN_LENGTH = 'lang.validations.subdomain_length'
    USERNAME_NO_SPACES = 'lang.validations.username.space_not_allowed'

    CREATED_SUCCESSFULLY = 'lang.created_successfully'
    DELETED_SUCCESSFULLY = 'lang.deleted_successfully'
    UPDATED_SUCCESSFULLY = 'lang.updated_successfully'
    SAVED_SUCCESSFULLY = 'lang.saved_successfully'
