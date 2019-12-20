from rest_framework.exceptions import APIException
from rest_framework import status
from ratelimit.exceptions import Ratelimited


class TransactionError(Exception):
    """Exception in combination with a transaction.
    """

    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors


class RpcConnectionError(TransactionError):
    """Exception in combination with wallet RPCs.
    """


class GetWalletError(TransactionError):
    """Exception in combination with
    getting/calculating the tarnsaction's amount.
    """


class GetWalletRPCError(APIException):
    status_code = 500
    default_detail = "RPC Error on getting wallet."


class GetBalanceError(APIException):
    status_code = 500
    default_detail = "RPC Error on getting balance."


class GetWalletAddressError(APIException):
    status_code = 500
    default_detail = "RPC Error on getting wallet address."


class GetAmountError(APIException):
    status_code = 500
    default_detail = "RPC Error on getting amount."


class MakeTransactionError(APIException):
    status_code = 500
    default_detail = "Could not make transaction."


class RatelimitedByWithdrawalsError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Sorry you are blocked."
