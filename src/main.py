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

        self.mm = MemoryManager(page_size, memory_size, disk_size)
        self.time = 0

    def run(self):
        pass

class MemoryManager:
    def __init__(self, page_size, memory_size, disk_size):
        self.page_size = page_size
        self.memory_size = memory_size
        self.disk_size = disk_size

        self.memory = []
        self.disk = []

        for _ in range (0, memory_size//page_size):
            self.memory.append(Page(page_size))

        for _ in range (0, disk_size//page_size):
            self.disk.append(Page(page_size))

    def add_process(self, process_name, process_size):
        remaining_size = process_size
        while remaining_size:
            current_page = None
            for page in self.memory:
                if page.is_idle:
                    current_page = page
                    break

            if remaining_size >= self.page_size:
                current_page.is_idle = False
                current_page.addresses = [process_name]*self.page_size
                remaining_size -= self.page_size

            # Just for test
            else:
                current_page.is_idle = False
                for i in range (0, remaining_size):
                    current_page.addresses[i] = process_name
                remaining_size = 0

                
    def print_state(self):
        print("\nMemory:")
        i=0
        for page in self.memory:
            print("{}\t{}\t{}".format(i,page.addresses, (i+self.page_size-1)))
            i += self.page_size

        print("\nDisk:")
        i=0
        for page in self.disk:
            print("{}\t{}\t{}".format(i,page.addresses, (i+self.page_size-1)))
            i += self.page_size      

class Page:
    def __init__(self, size):
        self.size = size
        self.idle_space = size
        self.is_idle = True
        self.addresses = [None]*self.size


class Process:
    def __init__(self, name, size):
        self.name = name
        self.size = size


if __name__ == "__main__":
    scheduler = reader.Reader("input.txt").read()

    print(scheduler.commands)
    scheduler.mm.print_state()
    scheduler.mm.add_process("p1", 24)
    scheduler.mm.print_state()