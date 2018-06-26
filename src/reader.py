from main import Scheduler

class Reader:
    def __init__(self, filename):
        self.file = open(filename)

    def read(self):
        mode = int(self.file.readline())
        swap_alg = int(self.file.readline())
        page_size = int(self.file.readline())
        memory_size = int(self.file.readline())
        disk_size = int(self.file.readline())
        commands = []

        # data format: AT BT P
        for line in self.file.readlines():
            line_data = []
            for x in line.split(" "):
                line_data.append(x)

            if len(line_data) == 3:
                commands.append((str(line_data[0]), str(line_data[1]), int(line_data[2])))

            elif len(line_data) == 2:
                commands.append((str(line_data[0]), str(line_data[1]).rstrip()))

        self.file.close()

        return Scheduler(mode, swap_alg, page_size, memory_size, disk_size, commands)