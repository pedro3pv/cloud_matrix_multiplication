from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api_services import process_matrix_multiplication


@api_view(['POST'])
def matrix_multiplication(request):
    result, status_code = process_matrix_multiplication(request.data)
    return Response(result, status=status_code)


def home(request):
    return render(request, 'home.html')