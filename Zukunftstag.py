#! python
# -*- coding: utf-8 -*-

# GUI fuer Gantry 
from Stepper import *
from tkinter import *
from tkinter import messagebox
from tkinter import font
from threading import *
import atexit
from time import sleep
import Limits
import re

class Gui():
    def __init__(self, root):
        """Do GUI stuff and attach to ObserverPattern"""
        self.root = root
        # Bind if you like to see Mouse Position
        #self.root.bind('<Motion>',self.callback)

        #Root Window
        self.root.title ("Zukunftstag")
        self.root.geometry("960x700+0+0")

        #Change default Textfont
        standart_font = font.nametofont("TkDefaultFont")
        standart_font.configure(size=16, family="Segoe UI")
        root.option_add("*Font", standart_font)
  
        #Label
        self.label_programm =           Label(root, text="Programm Code")     
        #Message
        self.message_anleitung = Message( root, justify= LEFT, 
                                                relief=RAISED, 
                                                width=355,
                                                text = "Steuere den Roboterarm mit nachfolgenden Befehlen:" + "\n" + 
                                                "X <Distanz in MM> für Horizontal" + "\n" +
                                                "Z <Distanz in MM> für Vertikal"   + "\n" +
                                                "SLEEP <Sekunden> für eine Pause"  + "\n")
        #Text entry
        self.text_entry = Text(root, width = 40, height = 20)
        self.text_entry.insert("1.0", "X 150")  
        #Buttons
        self.button_start =            Button(root, text="Start", fg="green", command=self.start_test, width = 20)
        self.button_nullpunkt =        Button(root, text="Nullpunkt", fg="orange", command=self.stop_test, width = 20)
        self.button_abbrechen =        Button(root, text="Abbrechen", fg="red" ,command=self.stop_test, width = 20)
        
        #Place all Tkinter elements
        space = 40
        self.label_programm.place             (x= 500, y = space*1)
        #Message
        self.message_anleitung.place          (x= 20, y = space*7)
        #Text
        self.text_entry.place                 (x= 500, y = space*2) 
        #Buttons
        self.button_start.place              (x= 20, y = space*1) 
        self.button_abbrechen.place          (x= 20, y = space*5)
        self.button_nullpunkt.place          (x= 20, y = space*3)
        #Init motors
        self.stepper_Z = Stepper("Z-axis", mm_per_step = 0.05, pin_dir = 35, pin_step = 31, polarity="normal", actual=0)
        self.stepper_X = Stepper("X-axis", mm_per_step = 0.22, pin_dir = 37, pin_step = 33, polarity="reversed", actual=0)

    def callback(self, e):
        """Show Mouse position"""
        x= e.x
        y= e.y
        print("Pointer is currently at %d, %d" %(x,y))

    def test_user_input(self, inStr, acttyp):
        """Check if string is digit"""
        if acttyp == '1': #insert
            if not inStr.isdigit():
                return False
        return True

    def move(self, commands):
        """Runs the stepper motors according commands list"""
        for command in commands:
            if self.stop_testing == True:
                return
            if command[0] == "X":
                self.stepper_X.goto_pos(command[1])
            elif command[0] == "Z":
                self.stepper_Z.goto_pos(command[1])
            elif command[0] == "SLEEP":
                self.stepper_X.pause(command[1])
            else:
                print("Fehler in Commands")
                
    def parser(self, user_programm):
        """Read string and extract commands. 
        commands[0] -> Axis commands[1] -> Distanze
        Returns: list"""
        arm_movement = []
        zeilen_counter = 0
        user_programm = user_programm.split("\n")       #Data now split to lines
        
        for line in user_programm:
            zeilen_counter += 1
            line = line.strip().upper()                 #Data remove trailing spaces and make upper-chase
            line = re.sub(' +', ' ', line)              #Data remove multi spaces
            commands = line.split(" ",1)                #Data split at space, max 1 split
            if commands[0] == "":
                continue
            if commands[0] in {'X','Z','SLEEP'} and commands[1].isnumeric():
                arm_movement.append([commands[0], int(commands[1])])
            else:
                print("Fehler in Programm Code")
                messagebox.showerror("Fehler", "Programm Fehler in Zeile: " + str(zeilen_counter))
        return(arm_movement)
       
    def start_test(self):
        """Start the movement, Configures Buttons, Start Thread"""
        print("Start")

        self.button_start.configure(state=DISABLED)
        self.stop_testing = False  

        arm_lenght = Limits.ARM_LEFT_RIGHT_MAX  # The free distanze to move at X-axis 
        arm_down =   Limits.ARM_UP_DOWN_MAX
        
        #Get text von Text entry
        user_programm = self.text_entry.get("1.0",'end-1c')
        arm_movement = self.parser(user_programm)

        t1 = Thread(target=self.move, args=(arm_movement,))
        t1.daemon = True
        t1.start()
        
    def stop_test(self):
        """Stops the movement, Runs the SteppersMotors to Zero."""
        print("Stopping...")
        self.stop_testing = True 
        self.stepper_X.stopping()
        self.stepper_Z.stopping()
        sleep(2)

        print(str(self.stepper_X.get_actual_steps()) + "STEPS")
        print(str(self.stepper_Z.get_actual_steps()) + "STEPS")
        self.stepper_Z.goto_pos(0)
        self.stepper_X.pause(5)
        self.stepper_X.goto_pos(0)
        self.button_start.configure(state=NORMAL)

        print("Stopped")

    def cleanup(self):
        """End APP, Show Messagebox: Null-Position"""
        print("Close GUI")
        finish = messagebox.askquestion("Abbruch", "Bitte nur beenden wenn Arm auf Null-Position steht " +"\n" +"\n"
                               + "Jetz zum Nullpunkt und Beenden ?")
        if finish == "yes":
            self.stop_test()
            self.root.destroy()


if __name__ == "__main__":

    root=Tk()
    gui = Gui(root)
    root.protocol('WM_DELETE_WINDOW',gui.cleanup)
    root.mainloop()

