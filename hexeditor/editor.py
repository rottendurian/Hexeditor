from hexeditor.dump import Hexdump
import curses

class Hexeditor(Hexdump):
    def __init__(self,filename,stdscr,width=16):
        super().__init__(filename)
        # self.width = width
        # self.page_length = int(curses.LINES / 1.5)
        # self.page_length = int(curses.LINES/2)

        self.cursor = self.file.tell()
        self.valid_inputs = {
            '0':0,'1':1,'2':2,'3':3,'4':4,'5':5,
            '6':6,'7':7,'8':8,'9':9,'a':10,'b':11,
            'c':12,'d':13,'e':14,'f':15,
        }
        self.stdscr = stdscr
    
    def update_page_length(self):
        self.page_length = int(curses.COLS/6)

    def move_cursor(self,offset):
        self.cursor+=offset
        if self.cursor >= self.file_size:
            self.cursor = self.file_size-1
            # return
        if self.cursor < 0:
            self.cursor = 0

        camera_offset = (self.cursor // self.page_length) - self.page_length//2
        if camera_offset > (self.file_size // self.page_length) - self.page_length:
            camera_offset = (self.file_size // self.page_length) - self.page_length-1
        if camera_offset < 0:
            camera_offset = 0

        self.camera = camera_offset*self.page_length
        
    
    def print_page(self,count):
        self.file.seek(self.camera,0)

        i = 0
        while i < count:
            line = self.dump_line()

            self.stdscr.addstr(f"{(self.camera+i*self.page_length):08X}: ")
            # if self.camera+i*self.page_length == self.cursor//self.page_length*self.page_length:
            #     self.stdscr.addstr(f"{0:010} ", curses.color_pair(1))
            # else:
            #   page offset in decimal
                
            if not line:
                break
            
            for k,b in enumerate(line):
                loc = self.camera+i*self.page_length + k
                if loc == self.cursor:
                    text = f"{b:02X}"
                    self.stdscr.addstr(text, curses.A_STANDOUT | curses.color_pair(1))#curses.color_pair(1))
                    self.stdscr.addstr(" ")
                else:
                    self.stdscr.addstr(f"{b:02X}")
                    self.stdscr.addstr(" ")
            #if length is less than 16, add spaces
            if len(line) < self.page_length:
                for j in range(self.page_length-len(line)):
                    self.stdscr.addstr("   ")
            self.stdscr.addstr("\t")
            for k,b in enumerate(line):
                loc = self.camera+i*self.page_length + k
                if loc == self.cursor:
                    text = chr(b) if b > 31 and b < 127 else "."
                    self.stdscr.addstr(text, curses.A_STANDOUT | curses.color_pair(1))
                    self.stdscr.addstr(" ")
                else:
                    self.stdscr.addstr(chr(b) if b > 31 and b < 127 else ".")
                    self.stdscr.addstr(" ")

            # self.stdscr.addstr("\n")
            #query to see if i+1 will fit on terminal
            y,x = self.stdscr.getmaxyx()
            if i+1 < y:
                self.stdscr.move(i + 1, 0)

            i+=1
        
        self.stdscr.refresh()
        self.file.seek(self.camera,0)
        
    def write_input(self,k1,k2):
        
        half_byte1 = self.valid_inputs[chr(k1)]
        half_byte2 = self.valid_inputs[chr(k2)]

        if half_byte1 is not None and half_byte2 is not None:
            byte = (half_byte1 << 4) + half_byte2
            self.write(self.cursor,bytes([byte]))
            self.move_cursor(1)
            