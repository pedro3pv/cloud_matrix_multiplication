import socketio
import sys
import time
import concurrent.futures
import uuid
from multiprocessing import cpu_count


class MatrixWorker:
    def __init__(self, server_url='http://localhost:5000', worker_id=None):
        self.server_url = server_url
        self.worker_id = worker_id or f"worker_{uuid.uuid4().hex[:8]}"
        self.sio = socketio.Client()
        self.is_connected = False
        self.tasks_processed = 0

        # Eventos SocketIO
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('worker_registered', self.on_registered)
        self.sio.on('execute_task', self.on_execute_task)

    def validate_matrix_structure(self, matrix, matrix_name):
        """Valida se a matriz tem estrutura retangular válida"""
        if not matrix:
            raise ValueError(f"{matrix_name} não pode estar vazia")

        if not isinstance(matrix, list):
            raise ValueError(f"{matrix_name} deve ser uma lista")

        if len(matrix) == 0:
            raise ValueError(f"{matrix_name} não pode ter zero linhas")

        # Verificar primeira linha
        if not isinstance(matrix[0], list):
            raise ValueError(f"Primeira linha de {matrix_name} deve ser uma lista")

        if len(matrix[0]) == 0:
            raise ValueError(f"Primeira linha de {matrix_name} não pode estar vazia")

        # Verificar se todas as linhas têm o mesmo tamanho
        expected_cols = len(matrix[0])
        for i, row in enumerate(matrix):
            if not isinstance(row, list):
                raise ValueError(f"Linha {i} de {matrix_name} deve ser uma lista")

            if len(row) != expected_cols:
                raise ValueError(f"Linha {i} de {matrix_name} tem {len(row)} colunas, esperado {expected_cols}")

            # Verificar se todos os elementos são números
            for j, element in enumerate(row):
                if not isinstance(element, (int, float)):
                    raise ValueError(
                        f"Elemento [{i}][{j}] de {matrix_name} deve ser um número, recebido {type(element)}")

        return True

    def multiply_matrices_chunk(self, matrix_a_chunk, matrix_b):
        """Multiplica um chunk da matriz A com matriz B completa usando paralelismo avançado"""

        try:
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

            # Criar lista de todas as multiplicações a serem realizadas
            tasks = [(i, j) for i in range(rows_a) for j in range(cols_b)]

            def compute_element(task):
                i, j = task
                current_sum = 0
                for k in range(cols_a):
                    if k >= len(matrix_b):
                        raise IndexError(f"Índice k={k} >= len(matrix_b)={len(matrix_b)}")
                    if j >= len(matrix_b[k]):
                        raise IndexError(f"Índice j={j} >= len(matrix_b[{k}])={len(matrix_b[k])}")
                    if k >= len(matrix_a_chunk[i]):
                        raise IndexError(f"Índice k={k} >= len(matrix_a_chunk[{i}])={len(matrix_a_chunk[i])}")
                    current_sum += matrix_a_chunk[i][k] * matrix_b[k][j]
                return (i, j, current_sum)

            # Usando ThreadPoolExecutor para dividir igualmente entre as threads
            result_matrix = [[0 for _ in range(cols_b)] for _ in range(rows_a)]
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for i, j, value in executor.map(compute_element, tasks):
                    result_matrix[i][j] = value

            print(f"[{self.worker_id}] Multiplicação paralela concluída com sucesso")
            return result_matrix

            print(f"[{self.worker_id}] Multiplicação paralela concluída com sucesso")
            return result

        except Exception as e:
            print(f"[{self.worker_id}] Erro detalhado na multiplicação:")
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
        """Callback de conexão"""
        print(f"[{self.worker_id}] Conectado ao servidor")
        self.is_connected = True

        # Registrar como worker
        self.sio.emit('worker_connect', {
            'worker_id': self.worker_id,
            'capabilities': {
                'cpu_cores': cpu_count(),
                'version': '1.1'
            }
        })

    def on_disconnect(self):
        """Callback de desconexão"""
        print(f"[{self.worker_id}] Desconectado do servidor")
        self.is_connected = False

        tentativas = 0
        while tentativas < 3 and not self.is_connected:
            tentativas += 1
            print(f"[{self.worker_id}] Tentando reconectar ({tentativas}/3)...")
            try:
                self.sio.connect(self.server_url)
                if self.is_connected:
                    print(f"[{self.worker_id}] Reconectado com sucesso!")
                    break
            except Exception as e:
                print(f"[{self.worker_id}] Falha ao reconectar: {e}")
                time.sleep(2)

    def on_registered(self, data):
        """Callback de registro confirmado"""
        print(f"[{self.worker_id}] Registrado no servidor: {data}")

    def on_execute_task(self, task_data):
        """Executa tarefa de multiplicação recebida"""
        print(f"[{self.worker_id}] Recebida tarefa: {task_data.get('subtask_id', 'unknown')}")

        try:
            start_time = time.time()

            # Extrair dados da tarefa com validação
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

            # Executar multiplicação
            result = self.multiply_matrices_chunk(matrix_a_chunk, matrix_b)

            execution_time = time.time() - start_time
            self.tasks_processed += 1

            # CORREÇÃO: Extrair task_id corretamente
            # Formato: uuid_startrow_endrow
            # Exemplo: 59a9f3a6-919c-4ce8-8b8e-e9ec57c5e01e_0_2
            subtask_parts = subtask_id.split('_')
            if len(subtask_parts) >= 3:
                # O UUID tem 5 partes separadas por hífen, juntar tudo exceto os últimos 2 elementos
                task_id = '_'.join(subtask_parts[:-2])
            else:
                task_id = subtask_id  # Fallback

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

            self.sio.emit('task_completed', response)
            print(f"[{self.worker_id}] Tarefa {subtask_id} completada em {execution_time:.3f}s")

        except Exception as e:
            print(f"[{self.worker_id}] Erro ao executar tarefa: {e}")

    def connect(self):
        """Conecta ao servidor"""
        try:
            print(f"[{self.worker_id}] Conectando a {self.server_url}...")
            self.sio.connect(self.server_url)
            return True
        except Exception as e:
            print(f"[{self.worker_id}] Erro ao conectar: {e}")
            return False

    def disconnect(self):
        """Desconecta do servidor"""
        if self.is_connected:
            self.sio.disconnect()

    def keep_alive(self):
        """Mantém worker ativo"""
        try:
            while self.is_connected:
                time.sleep(5)
                if self.is_connected:
                    # Enviar heartbeat
                    self.sio.emit('worker_heartbeat', {
                        'worker_id': self.worker_id,
                        'tasks_processed': self.tasks_processed,
                        'status': 'active'
                    })
        except KeyboardInterrupt:
            self.disconnect()


def main():
    # Configurações do worker
    server_url = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:5000'
    worker_id = sys.argv[2] if len(sys.argv) > 2 else None

    # Criar e iniciar worker
    worker = MatrixWorker(server_url, worker_id)

    if worker.connect():
        print(f"Worker {worker.worker_id}")

        try:
            worker.keep_alive()
        except KeyboardInterrupt:
            worker.disconnect()
    else:
        print("Falha ao conectar worker")
        sys.exit(1)


if __name__ == '__main__':
    main()
