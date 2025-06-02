from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import uuid
import time
import json
from collections import defaultdict
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'matrix_multiplication_secret'
socketio = SocketIO(app, cors_allowed_origins='*', logger=True, engineio_logger=True)


connected_workers = {}
pending_tasks = {}
completed_tasks = {}
task_results = defaultdict(dict)
def validate_matrix_complete(matrix):
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

class TaskManager:
    def __init__(self):
        self.lock = threading.Lock()

    def create_task(self, matrix_a, matrix_b):
        try:
            task_id = str(uuid.uuid4())

            if len(connected_workers) == 0:
                raise Exception("Nenhum worker conectado")

            if not matrix_a or not matrix_b:
                raise ValueError("Matrizes não podem estar vazias")

            if not isinstance(matrix_a, list) or not isinstance(matrix_b, list):
                raise ValueError("Matrizes devem ser listas")

            total_rows = len(matrix_a)
            if total_rows == 0:
                raise ValueError("Matriz A não pode ter zero linhas")

            num_workers = len(connected_workers)
            chunk_size = max(1, total_rows // num_workers)

            subtasks = []
            for i in range(0, total_rows, chunk_size):
                end_row = min(i + chunk_size, total_rows)
                subtask = {
                    'subtask_id': f"{task_id}_{i}_{end_row}",
                    'matrix_a_chunk': matrix_a[i:end_row],
                    'matrix_b': matrix_b,
                    'start_row': i,
                    'end_row': end_row,
                    'chunk_size': end_row - i
                }
                subtasks.append(subtask)

            with self.lock:
                pending_tasks[task_id] = {
                    'subtasks': subtasks,
                    'total_subtasks': len(subtasks),
                    'completed_subtasks': 0,
                    'result_matrix': [[0 for _ in range(len(matrix_b[0]))] for _ in range(len(matrix_a))],
                    'start_time': time.time(),
                    'status': 'pending'
                }

            return task_id, subtasks

        except Exception as e:
            print(f"Erro em create_task: {e}")
            return None, None

    def complete_subtask(self, task_id, subtask_id, result, start_row):
        print(f"DEBUG - complete_subtask: task_id={task_id}, start_row={start_row}")

        with self.lock:
            if task_id in pending_tasks:
                task = pending_tasks[task_id]
                print(f"DEBUG - Tarefa encontrada: {task['completed_subtasks']}/{task['total_subtasks']} completas")

                try:
                    for i, row in enumerate(result):
                        if start_row + i < len(task['result_matrix']):
                            task['result_matrix'][start_row + i] = row
                        else:
                            print(
                                f"ERRO - Índice fora dos limites: start_row={start_row}, i={i}, len={len(task['result_matrix'])}")
                            return False

                    task['completed_subtasks'] += 1
                    print(f"DEBUG - Progresso: {task['completed_subtasks']}/{task['total_subtasks']}")

                    if task['completed_subtasks'] >= task['total_subtasks']:
                        task['status'] = 'completed'
                        task['end_time'] = time.time()
                        completed_tasks[task_id] = pending_tasks.pop(task_id)
                        print(f"SUCESSO - Tarefa {task_id} totalmente completa!")
                        return True

                except Exception as e:
                    print(f"ERRO - Erro ao inserir resultado: {e}")
                    return False
            else:
                print(f"ERRO - Task ID {task_id} não encontrado em pending_tasks")
                print(f"DEBUG - Pending tasks disponíveis: {list(pending_tasks.keys())}")

        return False

task_manager = TaskManager()


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/api/multiply-matrices', methods=['POST'])
def multiply_matrices_distributed():
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type deve ser application/json'}), 400

        data = request.get_json()

        if not data or 'matrixA' not in data or 'matrixB' not in data:
            return jsonify({'error': 'JSON deve conter matrixA e matrixB'}), 400

        matrix_a = data['matrixA']
        matrix_b = data['matrixB']

        if not validate_matrix(matrix_a) or not validate_matrix(matrix_b):
            return jsonify({'error': 'Matrizes inválidas'}), 400

        if len(matrix_a[0]) != len(matrix_b):
            return jsonify({'error': 'Dimensões incompatíveis para multiplicação'}), 400

        if len(connected_workers) == 0:
            return jsonify({'error': 'Nenhum worker conectado'}), 503

        task_result = task_manager.create_task(matrix_a, matrix_b)

        if task_result is None or task_result == (None, None):
            return jsonify({'error': 'Falha ao criar tarefa distribuída'}), 500

        task_id, subtasks = task_result
        if task_id is None or subtasks is None:
            return jsonify({'error': 'Dados de tarefa inválidos'}), 500

        print(f"DEBUG - Tarefa criada: {task_id} com {len(subtasks)} subtasks")

        worker_list = list(connected_workers.keys())
        print(f"DEBUG - Workers disponíveis: {worker_list}")

        for i, subtask in enumerate(subtasks):
            worker_id = worker_list[i % len(worker_list)]
            print(f"DEBUG - Enviando subtask {subtask['subtask_id']} para worker {worker_id}")
            socketio.emit('execute_task', subtask, room=connected_workers[worker_id]['session_id'])

        timeout = 30
        start_time = time.time()

        while task_id in pending_tasks and (time.time() - start_time) < timeout:
            elapsed = time.time() - start_time
            if int(elapsed) % 5 == 0:
                remaining_tasks = pending_tasks[task_id]['total_subtasks'] - pending_tasks[task_id][
                    'completed_subtasks']
                print(f"DEBUG - Aguardando... {elapsed:.1f}s elapsed, {remaining_tasks} tasks restantes")
            time.sleep(0.1)

        if task_id in completed_tasks:
            result = completed_tasks[task_id]
            print(f"SUCESSO - Retornando resultado da tarefa {task_id}")
            return jsonify({
                'success': True,
                'result': result['result_matrix'],
                'workers_used': len(connected_workers),
                'execution_time': result['end_time'] - result['start_time'],
                'subtasks_completed': result['completed_subtasks']
            }), 200
        else:
            print(f"TIMEOUT - Tarefa {task_id} não completada a tempo")
            return jsonify({'error': 'Timeout na execução distribuída'}), 408

    except Exception as e:
        print(f"ERRO - Erro interno: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500


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


@socketio.on('worker_connect')
def handle_worker_connect(data):
    worker_id = data.get('worker_id', str(uuid.uuid4()))
    worker_info = {
        'worker_id': worker_id,
        'session_id': request.sid,
        'connected_at': time.time(),
        'tasks_completed': 0,
        'status': 'available'
    }

    connected_workers[worker_id] = worker_info
    emit('worker_registered', {'worker_id': worker_id, 'status': 'registered'})

    print(f"Worker {worker_id} conectado. Total workers: {len(connected_workers)}")


@socketio.on('task_completed')
@socketio.on('task_completed')
def handle_task_completed(data):
    print(f"DEBUG - Recebido task_completed: {data}")

    try:
        task_id = data.get('task_id')
        subtask_id = data.get('subtask_id')
        result = data.get('result')
        start_row = data.get('start_row')
        worker_id = data.get('worker_id')

        print(f"DEBUG - Processando: task_id={task_id}, subtask_id={subtask_id}, start_row={start_row}")

        if not all([task_id, subtask_id, result is not None, start_row is not None, worker_id]):
            print(f"ERRO - Dados incompletos recebidos do worker: {data}")
            return

        if worker_id in connected_workers:
            connected_workers[worker_id]['tasks_completed'] += 1
            connected_workers[worker_id]['status'] = 'available'
            print(
                f"DEBUG - Worker {worker_id} updated, tasks completed: {connected_workers[worker_id]['tasks_completed']}")

        is_complete = task_manager.complete_subtask(task_id, subtask_id, result, start_row)

        if is_complete:
            print(f"SUCESSO - Tarefa {task_id} completada por {len(connected_workers)} workers")
        else:
            print(f"DEBUG - Sub-tarefa {subtask_id} processada, aguardando outras...")

    except Exception as e:
        print(f"ERRO - Erro ao processar task_completed: {e}")
        import traceback
        traceback.print_exc()

@socketio.on('disconnect')
def handle_worker_disconnect():
    worker_to_remove = None
    for worker_id, worker_info in connected_workers.items():
        if worker_info['session_id'] == request.sid:
            worker_to_remove = worker_id
            break

    if worker_to_remove:
        del connected_workers[worker_to_remove]
        print(f"Worker {worker_to_remove} desconectado. Workers restantes: {len(connected_workers)}")


@app.route('/status')
def status():
    return jsonify({
        'workers_connected': len(connected_workers),
        'workers': {wid: {
            'tasks_completed': info['tasks_completed'],
            'status': info['status'],
            'connected_time': time.time() - info['connected_at']
        } for wid, info in connected_workers.items()},
        'pending_tasks': len(pending_tasks),
        'completed_tasks': len(completed_tasks)
    })


if __name__ == '__main__':
    if __name__ == '__main__':
        print("Servidor de multiplicação distribuída iniciado!")
        print("Workers podem se conectar em ws://localhost:5000")
        socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)
