class Hexdump:
    page_length = 16
    write_data = []
    def __init__(self,filename):
        self.filename = filename
        # Open file in binary mode r and w
        self.file = open(filename,"rb+")
        # Get file size
        self.file_size = self.file.seek(0,2)
        self.file.seek(0,0)
        # Set camera to current position
        self.camera = 0

    def __del__(self):
        self.file.close()
    
    def dump_line(self):
        # print(self.file.tell())
        line = self.file.read(self.page_length)
        
        if not line:
            return None
        return line

    def navigate(self,offset):
        if self.file.tell() + offset > self.file_size:
            print("Offset out of range")
            return
        self.file.seek(offset,1)

    def print_page(self,count):
        for i in range(count):
            line = self.dump_line()
            if not line:
                break
            for b in line:
                print(f"{b:02X}",end=" ")
            print("\t",end="")
            for b in line:
                print(chr(b) if b > 31 and b < 127 else ".",end=" ")
            print()
            
        self.file.seek(self.camera,0)
    
    def write(self,offset,byte):
        self.file.seek(offset,0)
        self.write_data.append((offset,self.file.read(1)))
        self.file.seek(offset,0)
        self.file.write(byte)
        self.file.seek(self.camera,0)
    
    def undo(self):
        if len(self.write_data) == 0:
            return
        offset,byte = self.write_data.pop()
        self.file.seek(offset,0)
        self.file.write(byte)
        self.file.seek(self.camera,0)

