# -*- coding: utf-8 -*-


class ValidationErrorBase(Exception):
    default_message = 'Validation error.'

    def __init__(self, message=None):
        super().__init__(message or self.default_message)


class TemperatureValidationError(ValidationErrorBase):
    default_message = 'Temperature is invalid.'
