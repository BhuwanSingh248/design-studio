
class AppException(Exception):
    def __init__(self, message:str):
        self.message = message
        super().__init__(self.message)

class LLMException(AppException):
    def __init__(self, message:str):
        super().__init__(message)

class LLMRateLimitError(LLMException):
    def __init__(self, message:str = "LLM rate limit exceeded"):
        super().__init__(message)

class LLMTimeoutError(LLMException):
    def __init__(self, message:str = "LLM timeout"):
        super().__init__(message)

class LLMServiceError(LLMException):
    def __init__(self, message:str):
        super().__init__(message)

class LLMAuthenticationError(LLMException):
    def __init__(self, message:str):
        super().__init__(message)

class LLMConfigurationError(LLMException):
    def __init__(self, message:str):
        super().__init__(message)

