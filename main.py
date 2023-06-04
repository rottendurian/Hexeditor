import hexeditor

if __name__ == "__main__":
    hexeditor.curses.wrapper(hexeditor.driver.driver)
    
    #if you are on windows, you will need to pip install windows-curses

    #arrow keys can be used to move around, 
    #z to undo, 
    #when ` is pressed, 
    #you can enter a number to move the cursor by that amount of bytes,
    #esc exits the program
    
    #known bug:
    #resizing the terminal window while in the program will bug out the display

    
    
    