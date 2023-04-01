import sys
import os
import curses

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
            
    
class HexdumpInteractive(Hexdump):
    def __init__(self,filename,stdscr):
        super().__init__(filename)
        self.cursor = self.file.tell()
        self.valid_inputs = {
            '0':0,'1':1,'2':2,'3':3,'4':4,'5':5,
            '6':6,'7':7,'8':8,'9':9,'a':10,'b':11,
            'c':12,'d':13,'e':14,'f':15,
        }
        self.stdscr = stdscr
    def move_cursor(self,offset):
        self.cursor+=offset
        if self.cursor >= self.file_size:
            self.cursor = self.file_size-1
            # return
        if self.cursor < 0:
            self.cursor = 0

        camera_offset = (self.cursor // 16) - 8
        if camera_offset > (self.file_size // 16) - 16:
            camera_offset = (self.file_size // 16) - 15
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
            


def main(stdscr):
    curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)

    args = sys.argv
    if len(args) < 2:
        print("Usage: {} filename".format(args[0]))
        return
    if not os.path.isfile(args[1]):
        print("File does not exist")
        return

    dump = HexdumpInteractive(args[1],stdscr)

    # Disable cursor blinking
    curses.curs_set(0)

    while True:
        curses.update_lines_cols()
        stdscr.clear()

        try:
            dump.print_page(16)
        except:
            pass

        key = stdscr.getch()

        # Update position based on user input
        if key == curses.KEY_UP:
            dump.move_cursor(-16)
        elif key == curses.KEY_DOWN:
            dump.move_cursor(16)
        elif key == curses.KEY_LEFT:
            dump.move_cursor(-1)
        elif key == curses.KEY_RIGHT:
            dump.move_cursor(1)
        elif key == 27:
            break
        elif chr(key) == 'z':
            dump.undo() 
        elif chr(key) == '`':
            buffer = ""
            while key != curses.KEY_ENTER and key != 10:
                key = stdscr.getch()
                if key == curses.KEY_ENTER or key == 10:
                    break
                if key == curses.KEY_UP:
                    if buffer.isnumeric():
                        dump.move_cursor(-int(buffer)*dump.page_length)
                    break
                elif key == curses.KEY_DOWN:
                    if buffer.isnumeric():
                        dump.move_cursor(int(buffer)*dump.page_length)
                    break
                elif key == curses.KEY_LEFT:
                    if buffer.isnumeric():
                        dump.move_cursor(-int(buffer))
                    break
                elif key == curses.KEY_RIGHT:
                    if buffer.isnumeric():
                        dump.move_cursor(int(buffer))
                    break
                buffer+=chr(key)
        else:
            if chr(key) in dump.valid_inputs:
                k1 = key
                k2 = stdscr.getch()
                if chr(k2) in dump.valid_inputs:
                    dump.write_input(k1,k2)

    curses.endwin()
                

if __name__ == "__main__":
    curses.wrapper(main)
    
    #if you are on windows, you will need to pip install windows-curses

    #arrow keys can be used to move around, 
    #z to undo, 
    #when ` is pressed, 
    #you can enter a number to move the cursor by that amount of bytes,
    #esc exits the program
    
    #known bug:
    #resizing the terminal window while in the program will bug out the display

    
    
    