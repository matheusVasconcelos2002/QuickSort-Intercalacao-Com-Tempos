import random
import heapq
import time
from collections import deque


# ============================================================
# CONFIGURAÇÕES DO PROGRAMA
# ============================================================

# Quantidade total de números que serão gerados
QUANTIDADE_NUMEROS = 100000

# Quantidade máxima de números que podem ser mantidos
# nas estruturas de processamento em memória
LIMITE_MEMORIA = 1000

# Quantidade de números armazenados em cada arquivo "parte"
TAMANHO_PARTE = 1000

# Quantidade de arquivos que serão intercalados por rodada
ARQUIVOS_POR_RODADA = 10

# Durante a intercalação, cada arquivo fornece somente
# 100 números por vez para a memória.
#
# 10 arquivos x 100 números = 1.000 números na memória
NUMEROS_POR_ARQUIVO_NA_RAM = 100


# ============================================================
# QUICK SORT
# ============================================================

# Função principal do QuickSort.
#
# O objetivo é ordenar uma lista utilizando o método
# de divisão e conquista:
#
# 1. Escolhe um pivô;
# 2. Organiza os valores menores antes do pivô;
# 3. Organiza os valores maiores depois do pivô;
# 4. Repete o processo nas duas partes.
def quicksort(lista, inicio=0, fim=None):

    # Na primeira chamada, "fim" recebe o índice do
    # último elemento da lista.
    if fim is None:
        fim = len(lista) - 1

    # Continua a ordenação enquanto houver pelo menos
    # dois elementos para comparar.
    if inicio < fim:

        # Organiza a lista em relação ao pivô e recebe
        # a posição definitiva em que o pivô ficou.
        indice_pivo = particionar(lista, inicio, fim)

        # Ordena recursivamente a parte que ficou
        # antes do pivô.
        quicksort(lista, inicio, indice_pivo - 1)

        # Ordena recursivamente a parte que ficou
        # depois do pivô.
        quicksort(lista, indice_pivo + 1, fim)


# Função responsável por realizar a partição da lista.
#
# O último elemento da região analisada é escolhido
# como pivô.
def particionar(lista, inicio, fim):

    # Escolhe o último elemento como pivô.
    pivo = lista[fim]

    # "i" representa a posição onde será colocado
    # o próximo elemento menor ou igual ao pivô.
    i = inicio - 1

    # Percorre os elementos da região analisada,
    # ignorando o próprio pivô.
    for j in range(inicio, fim):

        # Se o elemento atual for menor ou igual ao pivô,
        # ele deve ficar antes do pivô.
        if lista[j] <= pivo:

            i += 1

            # Troca as posições dos elementos.
            lista[i], lista[j] = lista[j], lista[i]

    # Coloca o pivô em sua posição definitiva.
    lista[i + 1], lista[fim] = lista[fim], lista[i + 1]

    # Retorna a posição final do pivô.
    return i + 1


# ============================================================
# ETAPA 1
# GERAR OS 100.000 NÚMEROS E CRIAR OS ARQUIVOS PARTE
# ============================================================

# Inicia a contagem do tempo total de execução.
tempo_inicio_total = time.perf_counter()


print("=" * 60)
print("ETAPA 1 - CRIAÇÃO DOS ARQUIVOS PARTE")
print("=" * 60)


# ------------------------------------------------------------
# GERAÇÃO DOS NÚMEROS
# ------------------------------------------------------------

# Gera 100.000 números diferentes.
#
# Os números são escolhidos aleatoriamente dentro do
# intervalo de 1 até 500.000.
#
# random.sample() garante que não haverá números repetidos.
numeros_gerados = random.sample(
    range(1, 500001),
    QUANTIDADE_NUMEROS
)


# Lista que armazenará os nomes dos arquivos criados.
arquivos_partes = []

# Controla quantos números já foram processados.
total_gerado = 0

# Controla a numeração dos arquivos.
numero_arquivo = 0


# Continua criando partes até que os 100.000 números
# tenham sido processados.
while total_gerado < QUANTIDADE_NUMEROS:

    # Define quantos números serão processados nesta parte.
    #
    # Normalmente serão 1.000, mas o min() também permite
    # tratar corretamente uma possível última parte menor.
    quantidade_atual = min(TAMANHO_PARTE, QUANTIDADE_NUMEROS - total_gerado)


    # --------------------------------------------------------
    # CARREGAMENTO DE UMA PARTE PARA PROCESSAMENTO
    # --------------------------------------------------------

    # Seleciona somente a parte atual dos números.
    #
    # Cada parte possui no máximo 1.000 números.
    memoria_ram = numeros_gerados[
        total_gerado:total_gerado + quantidade_atual
    ]


    # Verifica se a quantidade de números da parte
    # ultrapassou o limite definido.
    if len(memoria_ram) > LIMITE_MEMORIA:

        raise MemoryError(
            "O limite de 1.000 números na RAM foi ultrapassado!"
        )


    # --------------------------------------------------------
    # ORDENAÇÃO DA PARTE
    # --------------------------------------------------------

    # Ordena os números da parte utilizando o QuickSort.
    #
    # Depois dessa operação, os números dentro dessa
    # parte estarão em ordem crescente.
    quicksort(memoria_ram)


    # --------------------------------------------------------
    # GRAVAÇÃO DA PARTE NO DISCO
    # --------------------------------------------------------

    # Cria o nome do arquivo.
    #
    # O :03d faz com que a numeração tenha sempre
    # três dígitos:
    #
    # parte_000.txt
    # parte_001.txt
    # parte_002.txt
    # ...
    nome_arquivo = f"parte_{numero_arquivo:03d}.txt"


    # Abre o arquivo para escrita.
    with open(nome_arquivo, "w") as arquivo:

        # Grava cada número ordenado em uma linha.
        for numero in memoria_ram:

            arquivo.write(f"{numero}\n")


    # Guarda o nome do arquivo criado para que ele
    # possa ser utilizado nas próximas etapas.
    arquivos_partes.append(nome_arquivo)


    # Atualiza a quantidade total de números processados.
    total_gerado += len(memoria_ram)


    # Mostra na tela o arquivo criado e sua quantidade
    # de números.
    print(
        f"{nome_arquivo} -> "
        f"{len(memoria_ram)} números"
    )


    # Libera o conteúdo da parte que acabou de ser gravada.
    memoria_ram.clear()


    # Passa para o próximo arquivo.
    numero_arquivo += 1


# Libera a lista que continha os números gerados.
numeros_gerados.clear()


# Finaliza a contagem do tempo da Etapa 1.
tempo_fim_etapa1 = time.perf_counter()

tempo_etapa1 = tempo_fim_etapa1 - tempo_inicio_total


print()
print(f"Total gerado: {total_gerado}")
print(f"Arquivos parte criados: {len(arquivos_partes)}")
print(f"Tempo da Etapa 1: {tempo_etapa1:.4f} segundos")


# ============================================================
# FUNÇÃO PARA CARREGAR UM PEQUENO BLOCO DO ARQUIVO
# ============================================================

# Essa função lê uma quantidade limitada de números
# de um arquivo.
#
# Em vez de carregar o arquivo inteiro na memória,
# são carregados somente pequenos blocos.
def preencher_buffer(arquivo, quantidade):

    # deque funciona como uma fila.
    #
    # Ele permite remover rapidamente o primeiro elemento
    # utilizando popleft().
    buffer = deque()


    # Tenta ler a quantidade solicitada de números.
    for _ in range(quantidade):

        # Lê uma linha do arquivo.
        linha = arquivo.readline()


        # Se não houver mais linhas, significa que
        # chegamos ao final do arquivo.
        if not linha:
            break


        # Remove espaços/quebras de linha, transforma
        # o conteúdo em inteiro e adiciona ao buffer.
        buffer.append(int(linha.strip()))


    # Retorna os números carregados.
    return buffer


# ============================================================
# FUNÇÃO DE INTERCALAÇÃO
# ============================================================

# Essa função recebe vários arquivos que já estão ordenados
# e os intercala para produzir um único arquivo também ordenado.
#
# Para isso, utiliza:
#
# - buffers: armazenam pequenos blocos dos arquivos;
# - heap: identifica rapidamente o menor número disponível.
def intercalar_arquivos(
    arquivos_entrada,
    arquivo_saida,
    numeros_por_arquivo,
    limite_memoria
):

    # Guarda os arquivos que foram abertos.
    arquivos_abertos = []

    # Guarda o buffer correspondente a cada arquivo.
    buffers = []

    # Heap mínimo utilizado para encontrar o menor
    # número disponível entre os arquivos.
    heap = []

    # Controla a quantidade de números atualmente
    # carregados na memória.
    quantidade_na_memoria = 0


    # --------------------------------------------------------
    # ABERTURA DOS ARQUIVOS E CARREGAMENTO DOS BUFFERS
    # --------------------------------------------------------

    for indice, nome_arquivo in enumerate(arquivos_entrada):

        # Abre o arquivo para leitura.
        arquivo = open(nome_arquivo, "r")

        arquivos_abertos.append(arquivo)


        # Carrega somente uma pequena quantidade de números
        # desse arquivo.
        #
        # No nosso caso:
        # 100 números por arquivo.
        buffer = preencher_buffer(
            arquivo,
            numeros_por_arquivo
        )


        # Guarda o buffer na lista.
        buffers.append(buffer)


        # Atualiza a quantidade total de números na memória.
        quantidade_na_memoria += len(buffer)


        # Se o arquivo possui números, coloca o primeiro
        # deles no heap.
        #
        # O heap será responsável por descobrir qual é
        # o menor número entre os arquivos.
        if buffer:

            heapq.heappush(
                heap,
                (buffer[0], indice)
            )


    # --------------------------------------------------------
    # VERIFICAÇÃO DO LIMITE DE MEMÓRIA
    # --------------------------------------------------------

    # Verifica se a quantidade de números carregados
    # ultrapassou o limite estabelecido.
    if quantidade_na_memoria > limite_memoria:

        # Fecha os arquivos antes de interromper o programa.
        for arquivo in arquivos_abertos:

            arquivo.close()


        raise MemoryError(
            "O limite de 1.000 números na RAM foi ultrapassado!"
        )


    # Conta quantos números foram gravados no arquivo de saída.
    quantidade_escrita = 0


    # --------------------------------------------------------
    # INTERCALAÇÃO DOS ARQUIVOS
    # --------------------------------------------------------

    # Abre o arquivo de saída.
    with open(arquivo_saida, "w") as saida:

        # Continua enquanto existirem números no heap.
        while heap:

            # Retira do heap o menor número disponível.
            #
            # "numero" = valor encontrado
            # "indice" = arquivo de origem
            numero, indice = heapq.heappop(heap)


            # Grava o menor número no arquivo de saída.
            saida.write(f"{numero}\n")


            # Atualiza a quantidade de números gravados.
            quantidade_escrita += 1


            # Remove do buffer o número que acabou de ser usado.
            buffers[indice].popleft()


            # Como um número foi retirado da memória,
            # diminui a quantidade armazenada.
            quantidade_na_memoria -= 1


            # ------------------------------------------------
            # REABASTECIMENTO DO BUFFER
            # ------------------------------------------------

            # Se o buffer daquele arquivo ficou vazio,
            # significa que os números carregados já foram usados.
            if not buffers[indice]:

                # Busca mais 100 números diretamente do disco.
                novos_numeros = preencher_buffer(
                    arquivos_abertos[indice],
                    numeros_por_arquivo
                )


                # Adiciona os novos números ao buffer.
                buffers[indice].extend(
                    novos_numeros
                )


                # Atualiza a quantidade de números na memória.
                quantidade_na_memoria += len(
                    novos_numeros
                )


            # ------------------------------------------------
            # ADICIONAR O PRÓXIMO NÚMERO AO HEAP
            # ------------------------------------------------

            # Se ainda existem números no buffer,
            # pega o primeiro deles.
            if buffers[indice]:

                proximo = buffers[indice][0]


                # Coloca o próximo número no heap para
                # que ele possa ser comparado com os números
                # dos outros arquivos.
                heapq.heappush(
                    heap,
                    (proximo, indice)
                )


            # ------------------------------------------------
            # VERIFICAÇÃO DO LIMITE DE MEMÓRIA
            # ------------------------------------------------

            # Garante que o limite de memória continue
            # sendo respeitado durante a intercalação.
            if quantidade_na_memoria > limite_memoria:

                for arquivo in arquivos_abertos:

                    arquivo.close()


                raise MemoryError(
                    "O limite de memória foi ultrapassado!"
                )


    # --------------------------------------------------------
    # FECHAMENTO DOS ARQUIVOS
    # --------------------------------------------------------

    # Depois que todos os números foram processados,
    # fecha os arquivos de entrada.
    for arquivo in arquivos_abertos:

        arquivo.close()


    # Retorna a quantidade de números gravados.
    return quantidade_escrita


# ============================================================
# ETAPA 2
# INTERCALAÇÃO DOS ARQUIVOS DE 10 EM 10
# ============================================================

print()
print("=" * 60)
print("ETAPA 2 - CRIAÇÃO DOS ARQUIVOS TEMPORÁRIOS")
print("=" * 60)


# Lista que armazenará os nomes dos arquivos temporários.
arquivos_temporarios = []


# Inicia a contagem do tempo da Etapa 2.
tempo_inicio_temporarios = time.perf_counter()


# Percorre os arquivos de partes em grupos de 10.
#
# Como existem 100 arquivos:
#
# 100 arquivos ÷ 10 = 10 rodadas
for rodada in range(
    0,
    len(arquivos_partes),
    ARQUIVOS_POR_RODADA
):

    # Seleciona um grupo de até 10 arquivos.
    grupo = arquivos_partes[
        rodada:rodada + ARQUIVOS_POR_RODADA
    ]


    # Calcula o número da rodada.
    numero_rodada = (
        rodada // ARQUIVOS_POR_RODADA
    ) + 1


    # Define o nome do arquivo temporário.
    nome_temporario = (
        f"temp_rodada_{numero_rodada:03d}.txt"
    )


    print()
    print(f"RODADA {numero_rodada}")
    print("-" * 60)


    # Inicia a contagem do tempo da rodada.
    tempo_inicio_rodada = time.perf_counter()


    print("Arquivos utilizados:")


    # Mostra quais arquivos serão utilizados
    # naquela rodada.
    for arquivo in grupo:

        print(f"  {arquivo}")


    # --------------------------------------------------------
    # INTERCALAÇÃO DA RODADA
    #
    # 10 arquivos x 1.000 números
    # = 10.000 números no arquivo temporário
    #
    # Porém, somente:
    #
    # 10 arquivos x 100 números
    # = 1.000 números
    #
    # ficam carregados simultaneamente na memória.
    # --------------------------------------------------------

    quantidade = intercalar_arquivos(
        grupo,
        nome_temporario,
        NUMEROS_POR_ARQUIVO_NA_RAM,
        LIMITE_MEMORIA
    )


    # Guarda o nome do arquivo temporário criado.
    arquivos_temporarios.append(
        nome_temporario
    )


    # Calcula a quantidade esperada de números.
    esperado = (
        len(grupo) * TAMANHO_PARTE
    )


    print()

    print(
        f"{nome_temporario} criado!"
    )


    print(
        f"Números gravados: {quantidade}"
    )


    # Finaliza a contagem do tempo da rodada.
    tempo_fim_rodada = time.perf_counter()

    tempo_rodada = (
        tempo_fim_rodada - tempo_inicio_rodada
    )


    print(
        f"Números esperados: {esperado}"
    )


    print(
        f"Tempo da criação/intercalação: "
        f"{tempo_rodada:.4f} segundos"
    )


# Finaliza a contagem do tempo total da Etapa 2.
tempo_fim_temporarios = time.perf_counter()

tempo_temporarios = (
    tempo_fim_temporarios - tempo_inicio_temporarios
)


print()

print(
    f"Tempo total da Etapa 2 "
    f"(arquivos temporários): "
    f"{tempo_temporarios:.4f} segundos"
)


# ============================================================
# ETAPA 3
# INTERCALAÇÃO DOS ARQUIVOS TEMPORÁRIOS
# ============================================================

print()
print("=" * 60)
print("ETAPA 3 - RESULTADO FINAL")
print("=" * 60)


# Inicia a contagem do tempo da Etapa 3.
tempo_inicio_final = time.perf_counter()


# Nome do arquivo que armazenará o resultado final.
arquivo_final = "resultado_final.txt"


print()
print("Arquivos temporários utilizados:")


# Mostra os arquivos temporários que serão utilizados.
for arquivo in arquivos_temporarios:

    print(f"  {arquivo}")


# ------------------------------------------------------------
# INTERCALAÇÃO FINAL
#
# Existem:
#
# 10 arquivos temporários
# x
# 10.000 números
# =
# 100.000 números
#
# Novamente, somente 100 números de cada arquivo
# ficam carregados simultaneamente.
# ------------------------------------------------------------

quantidade_final = intercalar_arquivos(
    arquivos_temporarios,
    arquivo_final,
    NUMEROS_POR_ARQUIVO_NA_RAM,
    LIMITE_MEMORIA
)


print()

print(
    f"{arquivo_final} criado!"
)


print(
    f"Números gravados: {quantidade_final}"
)


print(
    f"Números esperados: {QUANTIDADE_NUMEROS}"
)


# Finaliza a contagem do tempo da Etapa 3.
tempo_fim_final = time.perf_counter()

tempo_etapa3 = (
    tempo_fim_final - tempo_inicio_final
)


print()

print(
    f"Tempo da Etapa 3 "
    f"(resultado final): "
    f"{tempo_etapa3:.4f} segundos"
)


# ============================================================
# ETAPA 4
# VERIFICAÇÃO DO RESULTADO FINAL
# ============================================================

print()
print("=" * 60)
print("ETAPA 4 - VERIFICAÇÃO")
print("=" * 60)


# Conta quantos números foram encontrados no arquivo final.
quantidade_lida = 0


# Assume inicialmente que o arquivo está ordenado.
ordenado = True


# Assume inicialmente que não existem números repetidos.
repetidos = False


# Guarda o número anterior para verificar a ordem crescente.
numero_anterior = None


# O set será utilizado para verificar números repetidos.
valores = set()


# Abre o arquivo final para leitura.
with open(arquivo_final, "r") as arquivo:

    # Percorre todos os números do arquivo.
    for linha in arquivo:

        # Converte a linha para inteiro.
        numero = int(linha.strip())


        # Conta mais um número lido.
        quantidade_lida += 1


        # ----------------------------------------------------
        # VERIFICAÇÃO DA ORDEM CRESCENTE
        # ----------------------------------------------------

        # Compara o número atual com o anterior.
        #
        # Se o atual for menor que o anterior,
        # significa que a ordem está incorreta.
        if (
            numero_anterior is not None
            and numero < numero_anterior
        ):

            ordenado = False


        # ----------------------------------------------------
        # VERIFICAÇÃO DE NÚMEROS REPETIDOS
        # ----------------------------------------------------

        # Verifica se o número atual já apareceu anteriormente.
        if numero in valores:

            repetidos = True


        # Adiciona o número ao conjunto de valores encontrados.
        valores.add(numero)


        # Atualiza o número anterior.
        numero_anterior = numero


# ============================================================
# RESULTADOS DA VERIFICAÇÃO
# ============================================================

print()


# Mostra quantos números foram encontrados.
print(
    f"Quantidade encontrada: {quantidade_lida}"
)


# Mostra quantos números eram esperados.
print(
    f"Quantidade esperada: {QUANTIDADE_NUMEROS}"
)


print()


# ------------------------------------------------------------
# VERIFICAÇÃO DA QUANTIDADE
# ------------------------------------------------------------

if quantidade_lida == QUANTIDADE_NUMEROS:

    print(
        "OK - Os 100.000 números estão presentes."
    )

else:

    print(
        "ERRO - A quantidade de números está incorreta."
    )


# ------------------------------------------------------------
# VERIFICAÇÃO DA ORDENAÇÃO
# ------------------------------------------------------------

if ordenado:

    print(
        "OK - Os números estão organizados "
        "em ordem crescente."
    )

else:

    print(
        "ERRO - Os números não estão ordenados."
    )


# ------------------------------------------------------------
# VERIFICAÇÃO DE REPETIÇÕES
# ------------------------------------------------------------

if not repetidos:

    print(
        "OK - Não existem números repetidos."
    )

else:

    print(
        "ERRO - Existem números repetidos."
    )


# ============================================================
# TEMPO TOTAL
# ============================================================

# Registra o momento em que todo o programa terminou.
tempo_fim_total = time.perf_counter()


# Calcula o tempo total de execução.
tempo_total = (
    tempo_fim_total - tempo_inicio_total
)


# ============================================================
# RESUMO FINAL
# ============================================================

print()
print("=" * 60)
print("PROCESSO FINALIZADO")
print("=" * 60)


print()

print(
    f"Arquivo final: {arquivo_final}"
)


print(
    f"Limite da RAM: {LIMITE_MEMORIA} números"
)


print()


# Tempo gasto na criação e ordenação das partes.
print(
    f"Tempo da Etapa 1: "
    f"{tempo_etapa1:.4f} segundos"
)


# Tempo gasto na criação dos arquivos temporários.
print(
    f"Tempo da Etapa 2 "
    f"(arquivos temporários): "
    f"{tempo_temporarios:.4f} segundos"
)


# Tempo gasto na criação do arquivo final.
print(
    f"Tempo da Etapa 3 "
    f"(resultado final): "
    f"{tempo_etapa3:.4f} segundos"
)


# Tempo total de execução do programa.
print(
    f"Tempo total de execução: "
    f"{tempo_total:.4f} segundos"
)