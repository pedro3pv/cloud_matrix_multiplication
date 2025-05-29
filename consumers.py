import json
from channels.generic.websocket import AsyncWebsocketConsumer


class MatrixDistributorConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.worker_group = "matrix_workers"
        self.available_workers = set()
        self.pending_jobs = []

    async def connect(self):
        # Adiciona worker ao grupo
        await self.channel_layer.group_add(
            self.worker_group,
            self.channel_name
        )

        # Adiciona à lista de workers disponíveis
        self.available_workers.add(self.channel_name)
        await self.accept()

        print(f"Worker conectado: {self.channel_name}")

    async def disconnect(self, close_code):
        # Remove worker do grupo
        await self.channel_layer.group_discard(
            self.worker_group,
            self.channel_name
        )

        # Remove da lista de workers disponíveis
        self.available_workers.discard(self.channel_name)
        print(f"Worker desconectado: {self.channel_name}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'worker_ready':
                # Worker está pronto para receber trabalho
                await self.handle_worker_ready()

            elif message_type == 'result':
                # Worker retornou resultado
                await self.handle_worker_result(data)

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Formato JSON inválido'
            }))

    async def handle_worker_ready(self):
        """Marca worker como disponível"""
        self.available_workers.add(self.channel_name)
        await self.send(text_data=json.dumps({
            'type': 'status',
            'message': 'Worker registrado como disponível'
        }))

    async def handle_worker_result(self, data):
        """Processa resultado do worker"""
        job_id = data.get('job_id')
        result = data.get('result')

        # Aqui você pode salvar o resultado, notificar cliente, etc.
        print(f"Resultado recebido para job {job_id}: {result}")

        # Marca worker como disponível novamente
        self.available_workers.add(self.channel_name)

    # Método para receber trabalho do sistema principal
    async def matrix_multiply_task(self, event):
        """Envia tarefa de multiplicação para o worker"""
        await self.send(text_data=json.dumps({
            'type': 'matrix_multiply',
            'job_id': event['job_id'],
            'matrixA': event['matrixA'],
            'matrixB': event['matrixB'],
            'block_info': event.get('block_info', {})
        }))

        # Remove worker da lista de disponíveis
        self.available_workers.discard(self.channel_name)
