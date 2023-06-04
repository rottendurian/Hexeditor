import sys
import os
import curses

from hexeditor.editor import Hexeditor

def driver(stdscr):
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

    dump = Hexeditor(args[1],stdscr)

    # Disable cursor blinking
    curses.curs_set(0)

    while True:
        curses.update_lines_cols()
        dump.update_page_length()
        stdscr.clear()

        try:
            dump.print_page(curses.LINES)
        except:
            pass

        key = stdscr.getch()

        # Update position based on user input
        if key == curses.KEY_UP:
            dump.move_cursor(-dump.page_length)
        elif key == curses.KEY_DOWN:
            dump.move_cursor(dump.page_length)
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
