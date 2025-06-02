import socketio
import json
import sys
import time
import threading
import uuid
from multiprocessing import cpu_count


class MatrixWorker:
    def __init__(self, server_url='http://localhost:5000', worker_id=None):
        self.server_url = server_url
        self.worker_id = worker_id or f"worker_{uuid.uuid4().hex[:8]}"
        self.sio = socketio.Client()
        self.is_connected = False
        self.tasks_processed = 0

        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('worker_registered', self.on_registered)
        self.sio.on('execute_task', self.on_execute_task)

    def validate_matrix_structure(self, matrix, matrix_name):
        if not matrix:
            raise ValueError(f"{matrix_name} não pode estar vazia")

        if not isinstance(matrix, list):
            raise ValueError(f"{matrix_name} deve ser uma lista")

        if len(matrix) == 0:
            raise ValueError(f"{matrix_name} não pode ter zero linhas")

        if not isinstance(matrix[0], list):
            raise ValueError(f"Primeira linha de {matrix_name} deve ser uma lista")

        if len(matrix[0]) == 0:
            raise ValueError(f"Primeira linha de {matrix_name} não pode estar vazia")

        expected_cols = len(matrix[0])
        for i, row in enumerate(matrix):
            if not isinstance(row, list):
                raise ValueError(f"Linha {i} de {matrix_name} deve ser uma lista")

            if len(row) != expected_cols:
                raise ValueError(f"Linha {i} de {matrix_name} tem {len(row)} colunas, esperado {expected_cols}")

            for j, element in enumerate(row):
                if not isinstance(element, (int, float)):
                    raise ValueError(
                        f"Elemento [{i}][{j}] de {matrix_name} deve ser um número, recebido {type(element)}")

        return True

    def multiply_matrices_chunk(self, matrix_a_chunk, matrix_b):
        try:
            print(f"[{self.worker_id}] DEBUG - Dimensões recebidas:")
            print(
                f"  matrix_a_chunk: {len(matrix_a_chunk) if matrix_a_chunk else 0} x {len(matrix_a_chunk[0]) if matrix_a_chunk and matrix_a_chunk[0] else 0}")
            print(
                f"  matrix_b: {len(matrix_b) if matrix_b else 0} x {len(matrix_b[0]) if matrix_b and matrix_b[0] else 0}")

            self.validate_matrix_structure(matrix_a_chunk, "matrix_a_chunk")
            self.validate_matrix_structure(matrix_b, "matrix_b")

            rows_a = len(matrix_a_chunk)
            cols_b = len(matrix_b[0])
            cols_a = len(matrix_a_chunk[0])
            rows_b = len(matrix_b)

            if cols_a != rows_b:
                raise ValueError(f"Dimensões incompatíveis: matrix_a_chunk cols ({cols_a}) != matrix_b rows ({rows_b})")

            print(
                f"[{self.worker_id}] DEBUG - Multiplicação: ({rows_a}x{cols_a}) x ({rows_b}x{cols_b}) = ({rows_a}x{cols_b})")

            result = [[0 for _ in range(cols_b)] for _ in range(rows_a)]

            for i in range(rows_a):
                for j in range(cols_b):
                    current_sum = 0
                    for k in range(cols_a):
                        if k >= len(matrix_b):
                            raise IndexError(f"Índice k={k} >= len(matrix_b)={len(matrix_b)}")

                        if j >= len(matrix_b[k]):
                            raise IndexError(f"Índice j={j} >= len(matrix_b[{k}])={len(matrix_b[k])}")

                        if k >= len(matrix_a_chunk[i]):
                            raise IndexError(f"Índice k={k} >= len(matrix_a_chunk[{i}])={len(matrix_a_chunk[i])}")

                        current_sum += matrix_a_chunk[i][k] * matrix_b[k][j]

                    result[i][j] = current_sum

            print(f"[{self.worker_id}] DEBUG - Multiplicação concluída com sucesso")
            return result

        except Exception as e:
            print(f"[{self.worker_id}] DEBUG - Erro detalhado na multiplicação:")
            print(f"  Erro: {str(e)}")
            print(f"  Tipo: {type(e).__name__}")

            try:
                print(
                    f"  matrix_a_chunk structure: {[len(row) if isinstance(row, list) else 'not-list' for row in matrix_a_chunk] if matrix_a_chunk else 'None'}")
                print(
                    f"  matrix_b structure: {[len(row) if isinstance(row, list) else 'not-list' for row in matrix_b] if matrix_b else 'None'}")
            except:
                pass

            raise e

    def on_connect(self):
        print(f"[{self.worker_id}] Conectado ao servidor")
        self.is_connected = True

        self.sio.emit('worker_connect', {
            'worker_id': self.worker_id,
            'capabilities': {
                'cpu_cores': cpu_count(),
                'version': '1.1'
            }
        })

    def on_disconnect(self):
        print(f"[{self.worker_id}] Desconectado do servidor")
        self.is_connected = False

    def on_registered(self, data):
        print(f"[{self.worker_id}] Registrado no servidor: {data}")

    def on_execute_task(self, task_data):
        print(f"[{self.worker_id}] Recebida tarefa: {task_data.get('subtask_id', 'unknown')}")

        try:
            start_time = time.time()

            if 'matrix_a_chunk' not in task_data:
                raise ValueError("Task data missing 'matrix_a_chunk'")
            if 'matrix_b' not in task_data:
                raise ValueError("Task data missing 'matrix_b'")
            if 'start_row' not in task_data:
                raise ValueError("Task data missing 'start_row'")
            if 'subtask_id' not in task_data:
                raise ValueError("Task data missing 'subtask_id'")

            matrix_a_chunk = task_data['matrix_a_chunk']
            matrix_b = task_data['matrix_b']
            start_row = task_data['start_row']
            subtask_id = task_data['subtask_id']

            result = self.multiply_matrices_chunk(matrix_a_chunk, matrix_b)

            execution_time = time.time() - start_time
            self.tasks_processed += 1

            subtask_parts = subtask_id.split('_')
            if len(subtask_parts) >= 3:
                task_id = '_'.join(subtask_parts[:-2])
            else:
                task_id = subtask_id

            print(f"[{self.worker_id}] DEBUG - subtask_id: {subtask_id}")
            print(f"[{self.worker_id}] DEBUG - task_id extraído: {task_id}")

            # Enviar resultado de volta
            response = {
                'task_id': task_id,
                'subtask_id': subtask_id,
                'result': result,
                'start_row': start_row,
                'worker_id': self.worker_id,
                'execution_time': execution_time,
                'chunk_size': len(matrix_a_chunk)
            }

            print(f"[{self.worker_id}] DEBUG - Enviando response: {response}")
            self.sio.emit('task_completed', response)
            print(f"[{self.worker_id}] Tarefa {subtask_id} completada em {execution_time:.3f}s")

        except Exception as e:
            print(f"[{self.worker_id}] Erro ao executar tarefa: {e}")

    def connect(self):
        try:
            print(f"[{self.worker_id}] Conectando a {self.server_url}...")
            self.sio.connect(self.server_url)
            return True
        except Exception as e:
            print(f"[{self.worker_id}] Erro ao conectar: {e}")
            return False

    def disconnect(self):
        if self.is_connected:
            self.sio.disconnect()

    def keep_alive(self):
        try:
            while self.is_connected:
                time.sleep(5)
                if self.is_connected:
                    self.sio.emit('worker_heartbeat', {
                        'worker_id': self.worker_id,
                        'tasks_processed': self.tasks_processed,
                        'status': 'active'
                    })
        except KeyboardInterrupt:
            print(f"[{self.worker_id}] Parando worker...")
            self.disconnect()


def main():
    server_url = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:5000'
    worker_id = sys.argv[2] if len(sys.argv) > 2 else None

    worker = MatrixWorker(server_url, worker_id)

    if worker.connect():
        print(f"Worker {worker.worker_id} pronto para receber tarefas!")
        print("Pressione Ctrl+C para parar")

        try:
            worker.keep_alive()
        except KeyboardInterrupt:
            print("\nParando worker...")
            worker.disconnect()
    else:
        print("Falha ao conectar worker")
        sys.exit(1)


if __name__ == '__main__':
    main()
