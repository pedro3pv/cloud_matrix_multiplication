def multiply_matrices(matrix_a, matrix_b):
    if len(matrix_a[0]) != len(matrix_b):
        raise ValueError("Número de colunas da matriz A deve ser igual ao número de linhas da matriz B")

    rows_a = len(matrix_a)
    cols_b = len(matrix_b[0])
    cols_a = len(matrix_a[0])

    result = [[0 for _ in range(cols_b)] for _ in range(rows_a)]

    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(cols_a):
                result[i][j] += matrix_a[i][k] * matrix_b[k][j]

    return result


def validate_matrix(matrix):
    if not isinstance(matrix, list) or len(matrix) == 0:
        return False

    row_length = len(matrix[0])
    for row in matrix:
        if not isinstance(row, list) or len(row) != row_length:
            return False
        for element in row:
            if not isinstance(element, (int, float)):
                return False

    return True
