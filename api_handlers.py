from rest_framework.response import Response
from rest_framework import status

from modules.matrix_operations import MatrixOperations


class MatrixAPIHandler:
    """Classe para lidar com operações da API de matrizes"""

    @staticmethod
    def multiply_matrices(request_data):
        """Processa a multiplicação de matrizes"""
        try:
            matrix_a = request_data.get('matrixA')
            matrix_b = request_data.get('matrixB')

            # Validar se as matrizes foram enviadas
            if not matrix_a or not matrix_b:
                return Response(
                    {'error': 'matrixA e matrixB são obrigatórios'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validar matrizes
            if not MatrixOperations.validate_matrix(matrix_a):
                return Response(
                    {'error': 'matrixA é inválida'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not MatrixOperations.validate_matrix(matrix_b):
                return Response(
                    {'error': 'matrixB é inválida'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Multiplicar as matrizes
            try:
                result = MatrixOperations.multiply(matrix_a, matrix_b)
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response({
                'matrixA': matrix_a,
                'matrixB': matrix_b,
                'result': result,
                'dimensions': {
                    'matrixA': MatrixOperations.get_dimensions(matrix_a),
                    'matrixB': MatrixOperations.get_dimensions(matrix_b),
                    'result': MatrixOperations.get_dimensions(result)
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Erro interno: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @staticmethod
    def add_matrices(request_data):
        """Processa a soma de matrizes"""
        try:
            matrix_a = request_data.get('matrixA')
            matrix_b = request_data.get('matrixB')

            if not matrix_a or not matrix_b:
                return Response(
                    {'error': 'matrixA e matrixB são obrigatórios'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            result = MatrixOperations.add(matrix_a, matrix_b)

            return Response({
                'matrixA': matrix_a,
                'matrixB': matrix_b,
                'result': result
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
