class BaseError(Exception):
    """Bazowa klasa błędów dla aplikacji Jules."""
    def __init__(self, message: str, details: str = None):
        super().__init__(message)
        self.message = message
        self.details = details

class InputError(BaseError):
    """Błąd walidacji danych wejściowych od użytkownika."""
    pass

class APIError(BaseError):
    """Błąd komunikacji z zewnętrznym API (np. OpenAI)."""
    pass

class SystemError(BaseError):
    """Wewnętrzny błąd systemowy (pliki, uprawnienia)."""
    pass
