"""统一异常定义（§6.2.4）。"""


class APIException(Exception):
    def __init__(self, code: int, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(APIException):
    def __init__(self, message: str = "资源不存在"):
        super().__init__(404, message, 404)


class UnauthorizedException(APIException):
    def __init__(self, message: str = "未授权"):
        super().__init__(401, message, 401)


class ForbiddenException(APIException):
    def __init__(self, message: str = "无权限"):
        super().__init__(403, message, 403)


class ConflictException(APIException):
    def __init__(self, message: str = "资源冲突"):
        super().__init__(409, message, 409)
