import random
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from pyshadow.main import Shadow

#Setting up geckowebdriver and loading webpage
driver = webdriver.Firefox()
shadow = Shadow(driver)
driver.get("https://www.powerlanguage.co.uk/wordle/")
time.sleep(1)
close_button = shadow.find_element(".close-icon")
close_button.click()
keyboard = shadow.find_element("#keyboard")

def enter_word(word):
    for l in word:
        keyboard.find_element(By.CSS_SELECTOR, "[data-key='"+l+"']").click()
    keyboard.find_element(By.CSS_SELECTOR, "[data-key='↵']").click()

f = open("official_wordle.txt")
word_list = f.readlines()

def get_word_from_dict(size):
    glist = []
    for word in word_list:
        if len(word)-1 == size:
            glist.append(word)
    i = random.randrange(0, len(glist))
    return glist[i][:len(glist[i])-1], glist


class Grid:
    def __init__(self,size = 5,tries = 6,word ='',web = 1):
        self.size = size
        if word == '':
            self.word, self.glist = get_word_from_dict(size)
        else:
            self.size = len(word)
            self.glist = get_word_from_dict(self.size)[1]
            self.word = word
        self.green = []
        self.yellow = []
        self.black = []
        self.inputs = []
        self.try_nb = 0
    
    def new_input(self, input:str):
        if len(input) != self.size:
            print("Wrong size!")
            return -1
        if not((input+'\n') in self.glist):
            print("Word doesn't exist")
            return -1
        if input == self.word:
            print("FOUND! in "+str(self.try_nb+1)+" tries")
            return 1

        self.inputs.append(input)
        self.try_nb += 1
        for i in range(0, len(input)):
            char = input[i]
            if char in self.word:
                if char == self.word[i]:
                    self.green.append((char,i))
                else:
                    self.yellow.append((char,i))
            else:
                self.black.append(char)
        
        #print("g:",self.green,"\ny:",self.yellow,"\nb:",self.black)

    def web_input(self, input: str):
        #submit input to the site and add a delay, word whould already be the right size
        enter_word(input)
        time.sleep(3)
        self.inputs.append(input)
        self.try_nb += 1
        nb_correct = 0
        #DONE: retrieve color data from current row from DOM and parse
        for i in range(0,self.size):
            tile = shadow.find_element(By.CSS_SELECTOR,"game-row:nth-child("+str(self.try_nb)+") > .row > game-tile:nth-child("+str(i+1)+") > .tile")
            color = tile.get_attribute("data-state")
            char = input[i]
            if color == "correct":
                self.green.append((char,i))
                nb_correct += 1
            if color == "present":
                self.yellow.append((char,i))
            if color == "absent":
                self.black.append(char)
            print(tile.get_attribute("data-state"))
        #if all correct stop
        if nb_correct == self.size:
            print("FOUND! Word was: "+input)
            return 1
        #if nbtry too high stop//DONE

    def solve_step(self):
        good1, good2, good3 = 0,0,0
        while good1 + good2 + good3 != 3:
            good1, good2, good3 = 1,1,1

            word = self.glist[random.randrange(0, len(self.glist))]
            word = word[:len(word) - 1]

            for (char,i) in self.green:
                if word[i] != char:
                    good1 = 0
            
            for (char,i) in self.yellow:
                if not(char in word):
                    good2 = 0
                if word[i] == char:
                    good2 = 0
            
            for char in self.black:
                if char in word:
                    good3 = 0
        print(word)
        #return self.new_input(word)
        return self.web_input(word)

grid = Grid()
while grid.solve_step() != 1 and grid.try_nb<6:
    pass

input("Press enter to close...")
try:
    driver.close()
except:
    pass