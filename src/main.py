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
from random import randint


TIME = 0


class Scheduler:
    def __init__(self, mode, swap_alg, page_size, memory_size, disk_size, commands=[]):
        # Mode: 0-Sequential, 1-Random
        self.mode = mode
        # Swap Algorithm: 0-LRU, 1-Random
        self.swap_alg = swap_alg

        self.page_size = page_size
        self.memory_size = memory_size
        self.disk_size = disk_size
        self.commands = commands

        self.mm = MemoryManager(page_size, memory_size, disk_size, swap_alg)

    def run(self):
        if self.mode == 0:
            self.run_commands()

    def run_commands(self):

        for command in self.commands:
            print("Time:", TIME)
            # Create a new process
            if command[0].upper() == 'C':
                print(
                    "\n----------------\nCreating process: {}\tSize: {}".format(command[1], command[2]))
                self.mm.add_process(command[1], command[2])
                self.mm.print_state()

            # Access process data
            elif command[0].upper() == 'A':
                print(
                    "\n----------------\nAccessing process: {}\tPos: {}".format(command[1], command[2]))
                self.mm.access(command[1], command[2], self.swap_alg)
                self.mm.print_state()

            # Allocate more memory to process
            elif command[0].upper() == 'M':
                print(
                    "\n----------------\nAllocating process: {}\tSize: {}".format(command[1], command[2]))
                self.mm.allocate(command[1], command[2])
                self.mm.print_state()

            # Terminate process
            elif command[0].upper() == 'T':
                print("--- Not implemented yet ---")

            else:
                print("--- ERROR: Invalid Command ---")

            add_clock()


class MemoryManager:
    def __init__(self, page_size, memory_size, disk_size, swap_alg):
        self.page_size = page_size
        self.memory_size = memory_size
        self.disk_size = disk_size
        self.swap_alg = swap_alg

        self.memory = []
        self.disk = []
        self.processes = {}

        for i in range(0, memory_size//page_size):
            self.memory.append(Page(page_size, (page_size*i), 'MEMORY'))

        for i in range(0, disk_size//page_size):
            self.disk.append(Page(page_size, (page_size*i), 'DISK'))

    def add_process(self, process_name, process_size):
        p = Process(process_name)
        self.processes[process_name] = p
        remaining_size = process_size

        free_space = 0
        for page in self.memory:
            if page.process == None:
                free_space += page.idle_space
        for page in self.disk:
            if page.process == None:
                free_space += page.idle_space
        if free_space < process_size:
            print("--- ERROR: Not enough memory to create process ---")
#            self.print_state()
            return
        
        i = 0
        while remaining_size:
            # Try to find a new empty page in memory
            current_page = None
            for page in self.memory:
                if not(page.process):
                    current_page = page
                    break

            # Found an empty memory page
            if current_page != None:
                current_page.process = p.name
                allocated = min(self.page_size, remaining_size)
                for _ in range(0, allocated):
                    current_page.add(p, i)
                    i += 1
                remaining_size -= allocated

            # Try to find disk space and swap
            elif self.has_empty_page(self.disk):
                for page in self.disk:
                    if not(page.process):
                        current_page = page
                        break
                swap_page = self.get_swap_candidate(self.swap_alg)
                print("Page Location: {}  Elements: {}  -  Swap Page Loc: {}  Elements: {}".format(
                    current_page.location, current_page.addresses, swap_page.location, swap_page.addresses))
                self.swap(swap_page, current_page)

            else:
                print("--- ERROR: Unknown flow error ---")
                break                

    def allocate(self, process_name, allocated):
        p = self.processes[process_name]
        remaining_size = allocated
        i = p.size

        free_space = 0
        for page in self.memory:
            if page.process == None or page.process == process_name:
                free_space += page.idle_space
        for page in self.disk:
            if page.process == None or page.process == process_name:
                free_space += page.idle_space
        if free_space < allocated:
            print("--- ERROR: Not enough memory to allocate process ---")
#            self.print_state()
            return

        
        while remaining_size:
            # In case there's still room in the latest process' page
            last_page = p.map[i-1][0]
            if last_page.idle_space > 0:
                last_page.add(p, i, )
                i += 1
                remaining_size -= 1
                continue

            # Try to find a new empty page in memory
            current_page = None
            for page in self.memory:
                if not(page.process):
                    current_page = page
                    break

            # Found an empty memory page
            if current_page != None:
                current_page.process = p.name
                current_page.add(p, i)
                i += 1
                remaining_size -= 1
                continue

            # Try to find disk space and swap
            elif self.has_empty_page(self.disk):
                for page in self.disk:
                    if not(page.process):
                        current_page = page
                        break
                swap_page = self.get_swap_candidate(self.swap_alg)
                print("Page Location: {}  Elements: {}  -  Swap Page Loc: {}  Elements: {}".format(
                    current_page.location, current_page.addresses, swap_page.location, swap_page.addresses))
                self.swap(swap_page, current_page)

            else:
                print("--- ERROR: Unknown flow error ---")
                break


    def access(self, process_name, address, swap_alg):
        p = self.processes[process_name]

        # Check if search is in valid range
        if not(0 <= address < p.size):
            print("--- ERROR: Invalid Address. Process: {} \tSize: {} \tRange: [0 - {}] ---".format(
                p.name, p.size, p.size-1))
            return False

        page = p.map[address][0]
        # Page is in already in memory
        if page.level == 'MEMORY':
            if page.process == p.name and page.addresses[p.map[address][1]] == address:
                print("Data succesfully accessed. Process: {} \tAddress: {} \tFound: {}-{}".format(
                    p.name, address, page.process, page.addresses[p.map[address][1]]))
                return True

        # Page is in disk (need to swap to memory)
        else:
            swap_page = self.get_swap_candidate(swap_alg)
            print("Page Location: {}  Elements: {}  -  Swap Page Loc: {}  Elements: {}".format(
                page.location, page.addresses, swap_page.location, swap_page.addresses))
            self.swap(swap_page, page)

    def swap(self, mem_page, disk_page):
        loc_1 = mem_page.location
        loc_2 = disk_page.location
        type_1 = mem_page.level
        type_2 = disk_page.level

        aux = mem_page
        for i in range(0, len(self.memory)):
            if self.memory[i] == mem_page:
                disk_page.location = loc_1
                disk_page.level = type_1
                self.memory[i] = disk_page
                break

        for i in range(0, len(self.disk)):
            if self.disk[i] == disk_page:
                aux.location = loc_2
                aux.level = type_2
                self.disk[i] = aux
                break



    def get_swap_candidate(self, swap_alg):
        if swap_alg == 0:
            return self.get_candidate_lru()
        elif swap_alg == 1:
            return self.get_candidate_random()

    # TODO: implement lru algorithm
    def get_candidate_lru(self):
        return self.memory[randint(0, 7)]

    # Return random memory page
    def get_candidate_random(self):
        return self.memory[randint(0, 7)]

    def has_empty_page(self, structure):
        for page in structure:
            if page.is_empty():
                return True
        return False

    def print_state(self):
        print("\nMemory:")

        for page in self.memory:
            print("{}\tProcess: {}\t{}\t{}".format(page.location, str(
                page.process), page.addresses, (page.location+self.page_size-1)))

        print("\nDisk:")

        for page in self.disk:
            print("{}\tProcess: {}\t{}\t{}".format(page.location, str(
                page.process), page.addresses, (page.location+self.page_size-1)))


class Page:
    def __init__(self, size, location, level):
        self.size = size
        self.idle_space = size
        self.level = level
        self.location = location
        self.process = None
        self.addresses = [None]*self.size
        self.last_used = None

    def add(self, process, process_address):
        self.addresses[self.size-self.idle_space] = process_address
        process.map[process_address] = (self, self.size - self.idle_space)
        self.idle_space -= 1
        process.size += 1
        self.last_used = TIME

    def is_empty(self):
        return self.size == self.idle_space


class Process:
    def __init__(self, name):
        self.name = name
        self.size = 0
        self.map = {}


def add_clock():
    global TIME
    TIME += 1


if __name__ == "__main__":
    scheduler = reader.Reader("input.txt").read()

    # print(scheduler.commands)
    scheduler.mm.print_state()
    # scheduler.mm.add_process("p1", 20)
    # scheduler.mm.add_process("p2", 15)
    # scheduler.mm.print_state()

    scheduler.run()
