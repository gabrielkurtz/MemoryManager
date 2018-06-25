# Pontifícia Universidade Católica do Rio Grande do Sul
# Escola Politécnica
# Disciplina de Sistemas Operacionais
# Prof. Avelino Zorzo
# ----------------------------
# Gabriel Ferreira Kurtz (Engenharia de Software)
# gabriel.kurtz@acad.pucrs.br

# Alexandre Araujo (Ciência da Computação)
# alexandre.henrique@acad.pucrs.br

# Maio/2018
# ----------------------------
# Simulador de Gerenciador de Memória

# Este programa foi desenvolvido para a disciplina de SisOp da FACIN
# (Escola Politécnica/PUCRS). Trata-se de um um script para simular
# um Gerenciador de Memória.

# O programa lê um imput de dados representando as características
# da memória do sistema (tamanho da página, tamanho da memória, tamanho
# alocado em disco) e deve simular as alocações de memória em dois modos:
# aleatório ou com comandos. Deve ser capaz de utilizar também dois
# algoritmos de trocas: LRU(Least Recently Used) ou aleatório.

import reader

class Scheduler:
    def __init__(self, mode, swap_alg, page_size, memory_size, disk_size, commands=[]):
        self.mode = mode
        self.swap_alg = swap_alg
        self.page_size = page_size
        self.memory_size = memory_size
        self.disk_size = disk_size
        self.commands = commands

        self.time = 0




if __name__ == "__main__":
    scheduler = reader.Reader("input.txt").read()

    print(scheduler.commands)
