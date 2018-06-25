# Pontifícia Universidade Católica do Rio Grande do Sul
# Escola Politécnica
# Disciplina de Sistemas Operacionais
# Prof. Avelino Zorzo
# ----------------------------
# Gabriel Ferreira Kurtz (Engenharia de Software)
# gabriel.kurtz@acad.pucrs.br

# Alexandre Araujo (Ciência da Computação)
# alexandre.henrique@acad.pucrs.br

# Junho/2018
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
        self.processes = {}

        for i in range (0, memory_size//page_size):
            self.memory.append(Page(page_size, (page_size*i), 'MEMORY'))

        for i in range (0, disk_size//page_size):
            self.disk.append(Page(page_size, (memory_size+(page_size*i)), 'DISK'))


    def add_process(self, process_name, process_size):
        p = Process(process_name, process_size)
        self.processes[process_name] = p
        remaining_size = process_size
        
        i=0
        while remaining_size:
            current_page = None
            for page in self.memory:
                if not(page.process):
                    current_page = page
                    break

            if current_page != None:
                current_page.process = p.name
                allocated = min(self.page_size, remaining_size)
                for _ in range(0, allocated):
                    current_page.add(p, i)
                    i += 1
                remaining_size -= allocated



    def print_state(self):
        print("\nMemory:")

        for page in self.memory:
            print("{}\tProcess: {}\t{}\t{}".format(page.location, str(page.process), page.addresses, (page.location+self.page_size-1)))

        print("\nDisk:")

        for page in self.disk:
            print("{}\tProcess: {}\t{}\t{}".format(page.location, str(page.process), page.addresses, (page.location+self.page_size-1)))


class Page:
    def __init__(self, size, location, level):
        self.size = size
        self.idle_space = size
        self.level = level
        self.location = location
        self.process = None
        self.addresses = [None]*self.size


    def add(self, process, process_address):
        self.addresses[self.size-self.idle_space] = process_address
        process.map[process_address] = self.location + self.size - self.idle_space - 1
        self.idle_space -= 1


class Process:
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.map = {}


if __name__ == "__main__":
    scheduler = reader.Reader("input.txt").read()

    print(scheduler.commands)
    scheduler.mm.print_state()
    scheduler.mm.add_process("p1", 20)
    scheduler.mm.add_process("p2", 15)
    scheduler.mm.print_state()