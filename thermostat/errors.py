# -*- coding: utf-8 -*-


class ValidationErrorBase(Exception):
    default_message = 'Validation error.'

    def __init__(self, message=None):
        super().__init__(message or self.default_message)


class UnitValidationError(ValidationErrorBase):
    default_message = 'Unknown unit.'


class TemperatureValidationError(ValidationErrorBase):
    default_message = 'Temperature is invalid.'
