import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


class PasswordValidator:
    def __init__(self, min_length=6):
        self.min_length = min_length

    def validate(self, password, user=None):
        password_pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[! @  # $%^&*()_+])[A-Za-z\d!@#$%^&*()_+]{6,}$'
        if re.match(password_pattern, password) is None:
            raise ValidationError(
                _("пароль — не менее %(min_length)d символов: как минимум одна заглавная буква, одна цифра и один специальный символ"),
                code="password_too_short",
                params={"min_length": self.min_length},
            )

    def get_help_text(self):
        return _(
            "пароль — не менее %(min_length)d символов: как минимум одна заглавная буква, одна цифра и один специальный символ."
            % {"min_length": self.min_length}
        )


@deconstructible
class UsernameValidator(validators.RegexValidator):
    regex = r"^[a-zA-Z][a-zA-Z0-9]{3,19}$"
    message = _(
        "логин — только латинские буквы и цифры, первый символ — буква, длина от 4 до 20 символов "
    )
    flags = 0
