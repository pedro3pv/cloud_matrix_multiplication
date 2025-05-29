from flask import Flask, render_template, request, jsonify

from modules.matrix_multiply import validate_matrix, multiply_matrices

app = Flask(__name__)

@app.route('/')
def hello_world():
    titulo = "Multiplicador de Matrizes"
    mensagem = "Bem-vindo ao multiplicador de matrizes!"
    return render_template('home.html', titulo=titulo, mensagem=mensagem)

@app.route('/api/multiply-matrices', methods=['POST'])
def multiply_matrices_endpoint():
    """
    Endpoint para multiplicar duas matrizes
    """
    try:
        # Verificar se o content-type é JSON
        if not request.is_json:
            return jsonify({'error': 'Content-Type deve ser application/json'}), 400

        # Obter dados JSON da requisição
        data = request.get_json()

        # Verificar se os campos obrigatórios estão presentes
        if not data or 'matrixA' not in data or 'matrixB' not in data:
            return jsonify({'error': 'JSON deve conter matrixA e matrixB'}), 400

        matrix_a = data['matrixA']
        matrix_b = data['matrixB']

        # Validar as matrizes
        if not validate_matrix(matrix_a):
            return jsonify({'error': 'matrixA não é uma matriz válida'}), 400

        if not validate_matrix(matrix_b):
            return jsonify({'error': 'matrixB não é uma matriz válida'}), 400

        # Multiplicar as matrizes
        result = multiply_matrices(matrix_a, matrix_b)

        # Retornar resultado
        return jsonify({
            'success': True,
            'matrixA': matrix_a,
            'matrixB': matrix_b,
            'result': result,
            'dimensions': {
                'matrixA': f"{len(matrix_a)}x{len(matrix_a[0])}",
                'matrixB': f"{len(matrix_b)}x{len(matrix_b[0])}",
                'result': f"{len(result)}x{len(result[0])}"
            }
        }), 200

    except ValueError as e:
        return jsonify({'error': f'Erro na multiplicação: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True)
