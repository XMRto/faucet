from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.generics import CreateAPIView
from django.http import JsonResponse

from ratelimit.mixins import RatelimitMixin

from django.conf import settings
from django.shortcuts import render

from .utils import tools
from .serializers import TransactionSerializer
from .exceptions import (
    MakeTransactionError,
    RatelimitedByWithdrawalsError,
    RpcConnectionError,
    GetWalletRPCError,
)

import logging

from .utils.wallet_rpc import WalletRPC, get_balance

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def index(request):
    """Render index.html template

    Configure text with monero network mode.
    Configure transaction endpoint with MONERO_ENDPOINT.
    """
    try:
        logger.info("Get network mode.")
        network_type = WalletRPC.get_network_type()
        network_type_other = ""
        if network_type == "stagenet":
            network_type_other = "testnet"
        elif network_type == "testnet":
            network_type_other = "stagenet"
        logger.info("Get wallet address.")
        wallet_address = WalletRPC.get_address()

        logger.info("Done getting RPC info.")

        return render(
            request,
            "transactions/index.html",
            {
                "wallet_address": wallet_address,
                "monero_network": network_type,
                "monero_network_other": network_type_other,
                "endpoint": settings.MONERO_ENDPOINT,
            },
        )
    except (RpcConnectionError) as e:
        return JsonResponse({"error": "Internal Server Error."}, status=500)


def get_client_ip(request):
    """Get the correct user IP address.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    # nginx
    x_real_ip = request.META.get("HTTP_X_REAL_IP")
    if x_real_ip:
        logger.debug("Took HTTP_X_REAL_IP")
        return x_real_ip
    elif x_forwarded_for:
        logger.debug("Took HTTP_X_FORWARDED_FOR")
        return x_forwarded_for.split(",")[-1].strip()
    else:
        logger.debug("Took REMOTE_ADDR")

        return request.META.get("REMOTE_ADDR")

    raise MakeTransactionError()


class TransactionsApiView(RatelimitMixin, CreateAPIView):
    """Transactions APIView providing GET and POST.

    GET: Get current balance of wallet.
    POST: Make a transaction to given XMR wallet address.
    Always returns repsonse in JSON.
    """

    # configure rate limit
    # ratelimit_key = 'ip'  # locally:
    ratelimit_key = "header:x-real-ip"  # behind proxy (nginx)
    ratelimit_rate = "1/{0}m".format(settings.ONCE_EVERY_N_MINUTE)
    ratelimit_method = "POST"
    ratelimit_block = True

    # set serializer for post data
    serializer_class = TransactionSerializer
    renderer_classes = (JSONRenderer,)

    def get(self, request, format=None):
        """Returns the current balance of the wallet.
        """
        return Response({"balance": int(tools.xmr_to_float(get_balance()))})

    def perform_create(self, serializer):
        ip_address = get_client_ip(self.request)
        serializer.validated_data.update(
            {"ip_address_hash": tools.hash_value(ip_address)}
        )
        serializer.save()
