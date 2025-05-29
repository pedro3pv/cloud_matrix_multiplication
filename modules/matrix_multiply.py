def multiply_matrices(matrix_a, matrix_b):
    """
    Multiplica duas matrizes
    """
    # Verificar se as matrizes podem ser multiplicadas
    if len(matrix_a[0]) != len(matrix_b):
        raise ValueError("Número de colunas da matriz A deve ser igual ao número de linhas da matriz B")

    # Dimensões da matriz resultado
    rows_a = len(matrix_a)
    cols_b = len(matrix_b[0])
    cols_a = len(matrix_a[0])

    # Inicializar matriz resultado com zeros
    result = [[0 for _ in range(cols_b)] for _ in range(rows_a)]

    # Multiplicação das matrizes
    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(cols_a):
                result[i][j] += matrix_a[i][k] * matrix_b[k][j]

    return result


def validate_matrix(matrix):
    """
    Valida se é uma matriz válida
    """
    if not isinstance(matrix, list) or len(matrix) == 0:
        return False

    # Verificar se todas as linhas têm o mesmo tamanho
    row_length = len(matrix[0])
    for row in matrix:
        if not isinstance(row, list) or len(row) != row_length:
            return False
        # Verificar se todos os elementos são números
        for element in row:
            if not isinstance(element, (int, float)):
                return False

    return True
