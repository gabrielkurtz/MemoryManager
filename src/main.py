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

        self.mm = MemoryManager(page_size, memory_size, disk_size)

    def run(self):
        if self.mode == 0:
            self.run_commands()

    def run_commands(self):
        
        for command in self.commands:
            print("Time:", TIME)
            # Create a new process
            if command[0].upper() == 'C':
                print("\n----------------\nCreating process: {}\tSize: {}".format(command[1], command[2]))
                self.mm.add_process(command[1], command[2])
                self.mm.print_state()
            
            # Access process data
            elif command[0].upper() == 'A':
                print("\n----------------\nAccessing process: {}\tPos: {}".format(command[1], command[2]))
                self.mm.access(command[1], command[2], self.swap_alg)
                self.mm.print_state()

            # Allocate more memory to process
            elif command[0].upper() == 'M':
                print("\n----------------\nAllocating process: {}\tSize: {}".format(command[1], command[2]))
                self.mm.allocate(command[1], command[2])
                self.mm.print_state()

            # Terminate process
            elif command[0].upper() == 'T':
                print("--- Not implemented yet ---")

            else:
                print("--- ERROR: Invalid Command ---")

            add_clock()
            
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
        p = Process(process_name)
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


    def allocate(self, process_name, allocated):
        p = self.processes[process_name]
        remaining_size = allocated
        i = p.size

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
            

    def access(self, process_name, address, swap_alg):
        p = self.processes[process_name]
        if not(0 < address < p.size-1):
            print("--- ERROR: Invalid Address. Process: {} \tSize: {} \tRange: [0 - {}] ---".format(p.name, p.size, p.size-1))
            return False
        
        page = p.map[address][0]
        if page.level == 'MEMORY':
            if page.process == p.name and page.addresses[p.map[address][1]] == address:
                print("Data succesfully accessed. Process: {} \tAddress: {} \tFound: {}-{}".format(p.name, address, page.process, page.addresses[p.map[address][1]]))
                return True


    def swap(page_1, page_2):
        loc_1 = page_1.location
        loc_2 = page_2.location
        type_1 = page_1.level
        type_2 = page_2.level


        aux_page = page_1
        page_1 = page_2
        page_2 = aux_page

        page_1.location = loc_1
        page_2.location = loc_2
        page_1.level = type_1
        page_2.level = type_2


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
        self.last_used = None


    def add(self, process, process_address):
        self.addresses[self.size-self.idle_space] = process_address
        process.map[process_address] = (self, self.size - self.idle_space)
        self.idle_space -= 1
        process.size += 1
        self.last_used = TIME


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