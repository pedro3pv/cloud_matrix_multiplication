import numpy as np

rows_A, cols_A = 300, 300

matriz_A = np.random.rand(rows_A, cols_A)

matriz_A_lista = matriz_A.tolist()

conteudo = f"\n{matriz_A_lista}\n\n"

with open('matriz_grande.txt', 'w') as arquivo:
    arquivo.write(conteudo)

print("Arquivo 'matriz_grande.txt' criado com as matrizes no formato solicitado.")
print(f"Dimensões das matrizes: A={matriz_A.shape}")
