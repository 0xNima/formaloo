from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_402_PAYMENT_REQUIRED, HTTP_400_BAD_REQUEST


class InsufficientFundException(APIException):
    status_code = HTTP_402_PAYMENT_REQUIRED
    default_detail = 'Payment Required. Your current balance is insufficient.'


class SelfPurchaseException(APIException):
    status_code = HTTP_400_BAD_REQUEST
    default_detail = 'Unable to process. Purchasing your own product is not allowed.'
