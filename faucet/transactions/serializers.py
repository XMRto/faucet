import logging

from rest_framework import serializers
from django.conf import settings
from django.core.validators import MinLengthValidator
from django.http import JsonResponse
from rest_framework import status

from .models import Transaction
from .exceptions import (
    RpcConnectionError,
    MakeTransactionError,
    RatelimitedByWithdrawalsError,
)

from .utils.wallet_rpc import WalletRPC, get_current_amount
from .utils import tools
from .utils.tools import is_monero_sub_or_address


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def wallet_address_validator(address):
    """Validate the destination address.

    :param address: the address to be validated
    :returns: the address if valid
    :raises serializers.ValidationError: if the address should not be valid
    """
    if not is_monero_sub_or_address(address):
        raise serializers.ValidationError("Not a Monero address.")
    return address


class TransactionSerializer(serializers.ModelSerializer):
    """Serializes fields of the actual transaction object.
    """

    destination_address = serializers.CharField(
        validators=[wallet_address_validator]
    )
    transaction_id = serializers.CharField(
        validators=[MinLengthValidator(64)], required=False
    )
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ("amount", "transaction_id", "destination_address")
        read_only_fields = ("amount", "transaction_id")

    def save(self, **kwargs):
        try:
            destination_address = self.validated_data.get(
                "destination_address"
            )
            if tools.addr_withdrew_too_often(
                destination_address=destination_address,
                rate_allowed=settings.ADDRESS_RATE_PER_DAY,
                days=1,
            ):
                logger.warning(
                    "Blocked by number of withdrawals per day limitation."
                )
                raise RatelimitedByWithdrawalsError
            transaction = WalletRPC.make_transaction(
                destination_address=destination_address,
                amount=get_current_amount(settings.FACTOR_BALANCE),
            )
            self.validated_data.update(transaction)
            logger.info("store tx {}".format(transaction))
            return super().save(**kwargs)
        except (ValueError, RpcConnectionError) as e:
            logger.error(str(e))
            raise MakeTransactionError(str(e))

    def get_amount(self, obj):
        return tools.xmr_to_float(obj.amount)
