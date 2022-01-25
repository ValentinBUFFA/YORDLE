import random
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from pyshadow.main import Shadow

# Setting up geckowebdriver and loading webpage
driver = webdriver.Firefox()  # change to webdriver.Chrome() to use with chrome
shadow = Shadow(driver)
driver.get("https://www.powerlanguage.co.uk/wordle/")
time.sleep(1)
keyboard = shadow.find_element("#keyboard")

#* Close starting pop up
close_button = shadow.find_element(".close-icon")
close_button.click()

f = open("wordlists/words_fetched.txt")
word_list = f.readlines()  # Note that every word ends with \n
f.close()


# Submit desired word to the wordle website
#
def enter_word(word):
    for l in word:
        keyboard.find_element(By.CSS_SELECTOR, "[data-key='"+l+"']").click()
    keyboard.find_element(By.CSS_SELECTOR, "[data-key='↵']").click()


# Returns list of words that match @size
# TODO strip \n from all words
#
def get_dict(size):
    glist = []
    for word in word_list:
        if len(word) - 1 == size:
            glist.append(word[:len(word)-1])
    return glist


class Grid:
    def __init__(self, size=5, tries=6, word='', web=1):
        self.size = size
        if web == 1:
            self.word = ''
            self.glist = get_dict(size)
        else:                                               # if in standalone mode take into account @word parameter
            if word == '':                                  # if @word is not specified get a random one with the right size
                self.glist = get_word_from_dict(size)
                self.word = self.glist[random.randrange(0, len(self.glist))]
            else:                                           # else use the specified word
                self.size = len(word)
                self.glist = get_dict(self.size)
                self.word = word

        self.green, self.green_index = [], []
        self.yellow, self.yellow_index = [], []
        self.black = []
        self.inputs = []
        self.try_nb = 0

    # * Only for standalone mode, useless when playing on website
    #  Simulates the behavior of the game
    #
    def new_input(self, input: str):
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
                    self.green.append(char)
                    self.green_index.append(i)
                else:
                    self.yellow.append(char)
                    self.yellow_index.append(i)
            else:
                if not(char in self.green):
                    self.black.append(char)

    # * For when using website
    #  Parses data from site html
    #
    def web_input(self, input: str):
        # Submit input to the site and add a delay
        enter_word(input)
        time.sleep(2) #! 2 seconds should work, if not change for an higher value

        # Update program data
        self.inputs.append(input)
        self.try_nb += 1
        nb_correct = 0

        # Retrieve color data from current row from DOM and parse
        for i in range(0, self.size):
            tile = shadow.find_element(By.CSS_SELECTOR, "game-row:nth-child("+str(
                self.try_nb)+") > .row > game-tile:nth-child("+str(i+1)+") > .tile")
            color = tile.get_attribute("data-state")
            char = input[i]

            if color == "correct":
                self.green.append(char)
                self.green_index.append(i)
                nb_correct += 1
                
            if color == "present":
                self.yellow.append(char)
                self.yellow_index.append(i)

            if color == "absent" and not(char in self.green) and not(char in self.yellow):
                self.black.append(char)

        if nb_correct == self.size:
            print("FOUND! Word was: "+input)
            return 1

    # * Find a word that complies with known data at current stage of the game
    #  Then test this word through one of the above methods
    #
    def solve_step(self):
        good1, good2, good3 = False, False, False
        while not(good1 and good2 and good3):
            good1, good2, good3 = True, True, True

            word = self.glist[random.randrange(0, len(self.glist))]

            for j in range(0, len(self.green)):
                (char, i) = (self.green[j], self.green_index[j])
                if word[i] != char:
                    good1 = False
                    break
            
            if good1: # Don't check if unnecessary 
                for j in range(0, len(self.yellow)):
                    (char, i) = (self.yellow[j], self.yellow_index[j])
                    if not(char in word) or word[i] == char:
                        good2 = False
                        break

                if good2: # Same
                    for char in self.black:
                        if char in word:
                            good3 = False
                            break
        print(word)

        # return self.new_input(word) #! use for standalone mode
        return self.web_input(word)


grid = Grid()
while grid.solve_step() != 1 and grid.try_nb < 6:
    pass

input("Press enter to close...")
try:
    driver.close()
except:
    pass
