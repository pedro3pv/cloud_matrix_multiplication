from rest_framework.views import APIView

from api_handlers import MatrixAPIHandler


class MatrixMultiplicationView(APIView):
    def post(self, request):
        return MatrixAPIHandler.multiply_matrices(request.data)

class MatrixAdditionView(APIView):
    def post(self, request):
        return MatrixAPIHandler.add_matrices(request.data)
