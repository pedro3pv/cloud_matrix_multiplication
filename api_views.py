import time

from rest_framework.views import APIView
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from api_handlers import MatrixAPIHandler
from modules.matrix_operations import MatrixOperations


class MatrixMultiplicationView(APIView):
    def post(self, request):
        matrixDistributionService = MatrixDistributionService()
        return matrixDistributionService.multiply_matrices_distributed(request.data)

class MatrixAdditionView(APIView):
    def post(self, request):
        return MatrixAPIHandler.add_matrices(request.data)


class MatrixDistributionService:
    def __init__(self):
        self.channel_layer = get_channel_layer()

    def multiply_matrices_distributed(self, request_data):
        """Distribui multiplicação de matrizes para workers"""
        try:
            matrix_a = request_data.get('matrixA')
            matrix_b = request_data.get('matrixB')

            # Validações existentes
            if not matrix_a or not matrix_b:
                return {
                    'error': 'matrixA e matrixB são obrigatórios',
                    'status': 400
                }

            if not MatrixOperations.validate_matrix(matrix_a):
                return {
                    'error': 'matrixA é inválida',
                    'status': 400
                }

            if not MatrixOperations.validate_matrix(matrix_b):
                return {
                    'error': 'matrixB é inválida',
                    'status': 400
                }

            # Gerar ID único para o job
            job_id = f"matrix_job_{int(time.time())}"

            # Enviar para workers via WebSocket
            async_to_sync(self.distribute_matrix_task)(job_id, matrix_a, matrix_b)

            return {
                'job_id': job_id,
                'message': 'Tarefa enviada para processamento distribuído',
                'status': 202
            }

        except Exception as e:
            print(e)
            return {
                'error': f'Erro interno: {str(e)}',
                'status': 500
            }

    async def distribute_matrix_task(self, job_id, matrix_a, matrix_b):
        """Distribui tarefa para workers disponíveis"""
        await self.channel_layer.group_send(
            "matrix_workers",
            {
                "type": "matrix_multiply_task",
                "job_id": job_id,
                "matrixA": matrix_a,
                "matrixB": matrix_b
            }
        )
