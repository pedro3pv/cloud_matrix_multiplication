import asyncio
import json
import websockets
import numpy as np
from websocket import create_connection
import time


class MatrixWorker:
    def __init__(self, server_url="ws://localhost:8000/ws/matrix/worker/"):
        self.server_url = server_url
        self.worker_id = f"worker_{int(time.time())}"

    def multiply_matrices(self, matrix_a, matrix_b):
        """Realiza a multiplicação das matrizes"""
        try:
            # Converte para numpy arrays
            np_a = np.array(matrix_a)
            np_b = np.array(matrix_b)

            # Multiplica as matrizes
            result = np.matmul(np_a, np_b)

            # Converte de volta para lista Python
            return result.tolist()

        except Exception as e:
            print(f"Erro na multiplicação: {e}")
            return None

    def run_worker_sync(self):
        """Execução síncrona do worker usando websocket-client"""
        print(f"Worker {self.worker_id} conectando ao servidor...")

        try:
            # Conexão WebSocket síncrona
            ws = create_connection(self.server_url)
            print(f"Worker {self.worker_id} conectado!")

            # Registra como worker disponível
            ws.send(json.dumps({
                'type': 'worker_ready',
                'worker_id': self.worker_id
            }))

            while True:
                try:
                    # Recebe mensagem do servidor
                    message = ws.recv()
                    data = json.loads(message)

                    if data.get('type') == 'matrix_multiply':
                        print(f"Recebida tarefa: {data.get('job_id')}")

                        # Processa multiplicação
                        matrix_a = data.get('matrixA')
                        matrix_b = data.get('matrixB')
                        job_id = data.get('job_id')

                        result = self.multiply_matrices(matrix_a, matrix_b)

                        if result is not None:
                            # Envia resultado de volta
                            response = {
                                'type': 'result',
                                'job_id': job_id,
                                'worker_id': self.worker_id,
                                'result': result,
                                'status': 'completed'
                            }
                            ws.send(json.dumps(response))
                            print(f"Resultado enviado para job {job_id}")
                        else:
                            # Envia erro
                            response = {
                                'type': 'result',
                                'job_id': job_id,
                                'worker_id': self.worker_id,
                                'error': 'Erro na multiplicação',
                                'status': 'error'
                            }
                            ws.send(json.dumps(response))

                        # Marca como disponível novamente
                        ws.send(json.dumps({
                            'type': 'worker_ready',
                            'worker_id': self.worker_id
                        }))

                except KeyboardInterrupt:
                    print("Worker interrompido pelo usuário")
                    break
                except Exception as e:
                    print(f"Erro no processamento: {e}")
                    time.sleep(1)  # Aguarda antes de tentar novamente

        except Exception as e:
            print(f"Erro de conexão: {e}")
        finally:
            try:
                ws.close()
            except:
                pass

    async def run_worker_async(self):
        """Execução assíncrona do worker usando websockets"""
        print(f"Worker {self.worker_id} conectando ao servidor...")

        try:
            async with websockets.connect(self.server_url) as websocket:
                print(f"Worker {self.worker_id} conectado!")

                # Registra como worker disponível
                await websocket.send(json.dumps({
                    'type': 'worker_ready',
                    'worker_id': self.worker_id
                }))

                async for message in websocket:
                    try:
                        data = json.loads(message)

                        if data.get('type') == 'matrix_multiply':
                            print(f"Recebida tarefa: {data.get('job_id')}")

                            # Processa multiplicação
                            matrix_a = data.get('matrixA')
                            matrix_b = data.get('matrixB')
                            job_id = data.get('job_id')

                            result = self.multiply_matrices(matrix_a, matrix_b)

                            if result is not None:
                                # Envia resultado de volta
                                response = {
                                    'type': 'result',
                                    'job_id': job_id,
                                    'worker_id': self.worker_id,
                                    'result': result,
                                    'status': 'completed'
                                }
                                await websocket.send(json.dumps(response))
                                print(f"Resultado enviado para job {job_id}")

                            # Marca como disponível novamente
                            await websocket.send(json.dumps({
                                'type': 'worker_ready',
                                'worker_id': self.worker_id
                            }))

                    except json.JSONDecodeError:
                        print("Erro ao decodificar JSON")
                    except Exception as e:
                        print(f"Erro no processamento: {e}")

        except Exception as e:
            print(f"Erro de conexão: {e}")


if __name__ == "__main__":
    worker = MatrixWorker()

    # Escolha entre execução síncrona ou assíncrona
    # worker.run_worker_sync()  # Versão síncrona
    asyncio.run(worker.run_worker_async())  # Versão assíncrona
