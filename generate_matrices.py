import numpy as np

rows_A, cols_A = 300, 300

# Gerar as matrizes aleatórias gigantes
matriz_A = np.random.rand(rows_A, cols_A)

# Converter as matrizes numpy para listas Python (formato [[1,2],[3,4]])
matriz_A_lista = matriz_A.tolist()

# Criar o conteúdo do arquivo
conteudo = f"\n{matriz_A_lista}\n\n"

# Salvar no arquivo matriz_grande.txt
with open('matriz_grande.txt', 'w') as arquivo:
    arquivo.write(conteudo)

print("Arquivo 'matriz_grande.txt' criado com as matrizes no formato solicitado.")
print(f"Dimensões das matrizes: A={matriz_A.shape}")
