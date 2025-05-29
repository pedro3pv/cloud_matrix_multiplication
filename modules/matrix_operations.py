class MatrixOperations:
    """Classe para operações com matrizes"""

    @staticmethod
    def validate_matrix(matrix):
        """Valida se é uma matriz válida"""
        if not matrix or not isinstance(matrix, list):
            return False

        if not all(isinstance(row, list) for row in matrix):
            return False

        # Verificar se todas as linhas têm o mesmo tamanho
        if len(set(len(row) for row in matrix)) > 1:
            return False

        return True

    @staticmethod
    def get_dimensions(matrix):
        """Retorna as dimensões da matriz (linhas, colunas)"""
        if not MatrixOperations.validate_matrix(matrix):
            return None
        return len(matrix), len(matrix[0])

    @staticmethod
    def can_multiply(matrix_a, matrix_b):
        """Verifica se duas matrizes podem ser multiplicadas"""
        if not MatrixOperations.validate_matrix(matrix_a) or not MatrixOperations.validate_matrix(matrix_b):
            return False

        rows_a, cols_a = MatrixOperations.get_dimensions(matrix_a)
        rows_b, cols_b = MatrixOperations.get_dimensions(matrix_b)

        return cols_a == rows_b

    @staticmethod
    def multiply(matrix_a, matrix_b):
        """Multiplica duas matrizes"""
        if not MatrixOperations.can_multiply(matrix_a, matrix_b):
            raise ValueError("Não é possível multiplicar essas matrizes - dimensões incompatíveis")

        rows_a, cols_a = MatrixOperations.get_dimensions(matrix_a)
        rows_b, cols_b = MatrixOperations.get_dimensions(matrix_b)

        # Criar matriz resultado
        result = [[0 for _ in range(cols_b)] for _ in range(rows_a)]

        # Multiplicação
        for i in range(rows_a):
            for j in range(cols_b):
                for k in range(cols_a):
                    result[i][j] += matrix_a[i][k] * matrix_b[k][j]

        return result

    @staticmethod
    def multiply_optimized(matrix_a, matrix_b):
        """Versão otimizada usando list comprehension"""
        if not MatrixOperations.can_multiply(matrix_a, matrix_b):
            raise ValueError("Não é possível multiplicar essas matrizes - dimensões incompatíveis")

        return [
            [
                sum(a * b for a, b in zip(row_a, col_b))
                for col_b in zip(*matrix_b)
            ]
            for row_a in matrix_a
        ]

    @staticmethod
    def add(matrix_a, matrix_b):
        """Soma duas matrizes"""
        if (MatrixOperations.get_dimensions(matrix_a) !=
                MatrixOperations.get_dimensions(matrix_b)):
            raise ValueError("Matrizes devem ter as mesmas dimensões para soma")

        rows, cols = MatrixOperations.get_dimensions(matrix_a)
        return [
            [matrix_a[i][j] + matrix_b[i][j] for j in range(cols)]
            for i in range(rows)
        ]

    @staticmethod
    def transpose(matrix):
        """Transpõe uma matriz"""
        if not MatrixOperations.validate_matrix(matrix):
            raise ValueError("Matriz inválida")

        return [[matrix[i][j] for i in range(len(matrix))]
                for j in range(len(matrix[0]))]

    @staticmethod
    def display(matrix):
        """Exibe a matriz de forma formatada"""
        if not MatrixOperations.validate_matrix(matrix):
            return "Matriz inválida"

        return '\n'.join([' '.join(map(str, row)) for row in matrix])


# Classe alternativa usando métodos de instância
class Matrix:
    """Classe que representa uma matriz como objeto"""

    def __init__(self, data):
        if not MatrixOperations.validate_matrix(data):
            raise ValueError("Dados de matriz inválidos")
        self.data = data
        self.rows, self.cols = MatrixOperations.get_dimensions(data)

    def multiply(self, other):
        """Multiplica esta matriz por outra"""
        if isinstance(other, Matrix):
            other_data = other.data
        else:
            other_data = other

        result = MatrixOperations.multiply(self.data, other_data)
        return Matrix(result)

    def add(self, other):
        """Soma esta matriz com outra"""
        if isinstance(other, Matrix):
            other_data = other.data
        else:
            other_data = other

        result = MatrixOperations.add(self.data, other_data)
        return Matrix(result)

    def transpose(self):
        """Retorna a transposta desta matriz"""
        result = MatrixOperations.transpose(self.data)
        return Matrix(result)

    def __str__(self):
        return MatrixOperations.display(self.data)

    def to_list(self):
        """Retorna os dados como lista"""
        return self.data
