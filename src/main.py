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

# Input file
INPUT_FILE = "input_random.txt"
#INPUT_FILE = "input.txt"

# Chance for random process to allocate more memory
PROC_ALLOCATE = 25
# Chance for random process to terminate
PROC_TERMINATE = 15

# Global time variable
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
        add_clock()
        if self.mode == 0:
            self.run_commands()
        elif self.mode == 1:
            self.run_random()
        else:
            print("--- ERROR: Unknown mode. 0-Sequential, 1-Random ---")
        

    def run_commands(self):

        for command in self.commands:
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
                self.mm.access(command[1], command[2])
                self.mm.print_state()

            # Allocate more memory to process
            elif command[0].upper() == 'M':
                print(
                    "\n----------------\nAllocating process: {}\tSize: {}".format(command[1], command[2]))
                self.mm.allocate(command[1], command[2])
                self.mm.print_state()

            # Terminate process
            elif command[0].upper() == 'T':
                print(
                    "\n----------------\nTerminating process: {}".format(command[1]))
                self.mm.terminate(command[1])
                self.mm.print_state()

            else:
                print("--- ERROR: Invalid Command ---")

            add_clock()

    def run_random(self):
        print("\nTime:", TIME-1)
        
        total_memory = self.disk_size + self.memory_size
        starting_memory = total_memory/3

        # Start processes until memory and disk are reasonably full
        i = 1
        while starting_memory > 0:
            new_process_name = "p" + str(i)
            new_process_size = randint(1,(starting_memory//2)+1)
            print("\n----------------\nCreating process: {}\tSize: {}".format(new_process_name, new_process_size))    
            self.mm.add_process(new_process_name, new_process_size)
            self.mm.print_state()
            starting_memory -= new_process_size
            i += 1
            add_clock()

        while self.mm.processes:
            copy_processes = dict(self.mm.processes)
            for process in copy_processes:
                
                if randint(0,99) < PROC_TERMINATE:
                    print("\n----------------\nTerminating process: {}".format(process))
                    self.mm.terminate(process)
                    self.mm.print_state()
                    add_clock()

                elif randint(0,99) < PROC_ALLOCATE:
                    size = randint(1, total_memory//4)
                    print("\n----------------\nAllocating process: {}\tSize: {}".format(process, size))
                    self.mm.allocate(process, size)
                    self.mm.print_state()
                    add_clock()               

                else:
                    size = self.mm.processes[process].size
                    pos = randint(0,size-1)
                    print("\n----------------\nAccessing process: {}\tPos: {}".format(process, pos))
                    self.mm.access(process, pos)
                    self.mm.print_state()
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
                self.swap(swap_page, current_page)

            else:
                print("--- ERROR: Unknown flow error ---")
                break


    def access(self, process_name, address):
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
                page.last_used = TIME
                return True

        # Page is in disk (need to swap to memory)
        else:
            swap_page = self.get_swap_candidate(self.swap_alg)
            self.swap(swap_page, page)

    
    def swap(self, mem_page, disk_page):
        loc_1 = mem_page.location
        loc_2 = disk_page.location
        type_1 = mem_page.level
        type_2 = disk_page.level

        print("Page Fault - Swapping Pages\nPage 1 - Location: {} {}\tUsed: {}  Elements: {} {}\nPage 2 - Location: {} {}\tUsed: {}  Elements: {} {}".format(
                mem_page.level, mem_page.location, mem_page.last_used, mem_page.process, mem_page.addresses, 
                disk_page.level, disk_page.location, disk_page.last_used, disk_page.process, disk_page.addresses))

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

    # Return least recently used page
    def get_candidate_lru(self):
        lru_page = self.memory[0]
        lru_time = self.memory[0].last_used
        
        for page in self.memory:
            if page.last_used < lru_time:
                lru_page = page
                lru_time = page.last_used
        
        return lru_page

    # Return random memory page
    def get_candidate_random(self):
        return self.memory[randint(0, 7)]

    def terminate(self, process_name):
        for i in range(0, self.memory_size//self.page_size):
            if self.memory[i].process == process_name:
                aux = self.memory[i]
                self.memory[i]=Page(self.page_size, aux.location, 'MEMORY')

        for i in range(0, self.disk_size//self.page_size):
            if self.disk[i].process == process_name:
                aux = self.disk[i]
                self.disk[i]=Page(self.page_size, aux.location, 'DISK')
    
        self.processes.pop(process_name, None)

    def has_empty_page(self, structure):
        for page in structure:
            if page.is_empty():
                return True
        return False

    def print_state(self):
        print("\nMemory:")

        for page in self.memory:
            print("Process: {}\tLast Use: {}\t{}\t{}\t{}".format(str(page.process), page.last_used, page.location, page.addresses, (page.location+self.page_size-1)))

        print("\nDisk:")

        for page in self.disk:
            print("Process: {}\tLast Use: {}\t{}\t{}\t{}".format(str(page.process), page.last_used, page.location, page.addresses, (page.location+self.page_size-1)))

        print("\nTime:", TIME)


class Page:
    def __init__(self, size, location, level):
        self.size = size
        self.idle_space = size
        self.level = level
        self.location = location
        self.process = None
        self.addresses = [None]*self.size
        self.last_used = TIME

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
    scheduler = reader.Reader(INPUT_FILE).read()
    scheduler.mm.print_state()
    scheduler.run()
