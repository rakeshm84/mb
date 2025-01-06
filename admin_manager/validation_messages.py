from django.utils.translation import gettext_lazy as _

class ValidationMessages:
    USERNAME_REQUIRED = 'lang.validations.username.required'
    USERNAME_NOT_UNIQUE = 'lang.validations.username.not_unique'
    
    EMAIL_REQUIRED = 'lang.validations.email.required'
    EMAIL_INVALID = 'lang.validations.email.invalid'
    EMAIL_NOT_UNIQUE = 'lang.validations.email.not_unique'

    PASSWORD_REQUIRED = 'lang.validations.password.required'
    PASSWORD_UPPERCASE = 'lang.validations.password.contains_uppercase'
    PASSWORD_LOWERCASE = 'lang.validations.password.contains_lowercase'
    PASSWORD_DIGIT = 'lang.validations.password.contains_digit'
    PASSWORD_SPECIAL_CHAR = 'lang.validations.password.contains_special_char'

    FIRST_NAME_REQUIRED = 'lang.validations.first_name_required'
    FIRST_NAME_NOT_VALID = 'lang.validations.first_name_not_valid'
    LAST_NAME_REQUIRED = 'lang.validations.last_name_required'
    LAST_NAME_NOT_VALID = 'lang.validations.last_name_not_valid'
