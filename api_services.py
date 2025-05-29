from modules.matrix_operations import MatrixOperations


def process_matrix_multiplication(data):
    """Função simples para processar multiplicação de matrizes"""
    try:
        matrix_a = data.get('matrixA')
        matrix_b = data.get('matrixB')

        if not matrix_a or not matrix_b:
            return {'error': 'matrixA e matrixB são obrigatórios'}, 400

        if not MatrixOperations.validate_matrix(matrix_a) or not MatrixOperations.validate_matrix(matrix_b):
            return {'error': 'Uma das matrizes é inválida'}, 400

        result = MatrixOperations.multiply(matrix_a, matrix_b)

        return {
            'matrixA': matrix_a,
            'matrixB': matrix_b,
            'result': result
        }, 200

    except ValueError as e:
        return {'error': str(e)}, 400
    except Exception as e:
        return {'error': f'Erro interno: {str(e)}'}, 500
