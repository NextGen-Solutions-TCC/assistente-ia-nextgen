import logging

from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('Api')


def custom_exception_handler(exc, context):

    response = drf_exception_handler(exc, context)

    if response is not None:
        return response

    logger.exception('Erro não tratado em %s', context.get('view'))

    return Response(
        {'detail': 'Erro interno do servidor. Tente novamente mais tarde.'},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )