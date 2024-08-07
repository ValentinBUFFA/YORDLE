import random
import time

from pyshadow.main import Shadow
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


# Setting up geckowebdriver and loading webpage
driver = webdriver.Firefox()  # change to webdriver.Chrome() to use with chrome/chromium
shadow = Shadow(driver)
driver.get("https://www.nytimes.com/games/wordle/index.html")
time.sleep(10)
keyboard = shadow.find_element("[aria-label='Keyboard']")

#* Close starting pop up
#close_button = shadow.find_element(".close-icon")
#close_button.click()

f = open("wordlists/words_fetched.txt")
word_list = f.readlines()  # Note that every word ends with \n, it is later stripped in get_dict()
f.close()


# Submit desired @word to the wordle website
#TODO try alternative method using sendkeys() (might not work)
def enter_word(word):
    for l in word:
        keyboard.find_element(By.CSS_SELECTOR, "[data-key='"+l+"']").click()
    keyboard.find_element(By.CSS_SELECTOR, "[data-key='↵']").click()


# Returns list of words that match @size
#
def get_dict(size):
    glist = []
    for word in word_list:
        if len(word) - 1 == size:
            glist.append(word[:len(word)-1])
    return glist


# ? IS web OPTION STILL USEFUL
class Grid:
    # @size is the size of the word, not needed if @word is not empty
    # @tries is the limit of tries before losing the game
    # @word is only useful when trying to make the program guess a word you want
    # @web defines if you want to query information from the webapp or play the game standalone
    #TODO do not load selenium when web == 0
    def __init__(self, size=5, tries=6, word='', web=1):
        self.size = size
        if web == 1:
            self.word = ''
            self.glist = get_dict(size)
        else:                                               # if in standalone mode take into account @word parameter
            if word == '':                                  # if @word is not specified get a random one with the right size
                self.glist = get_dict(size)
                self.word = self.glist[random.randrange(0, len(self.glist))]
            else:                                           # else use the specified word
                self.size = len(word)
                self.glist = get_dict(self.size)
                self.word = word

        self.green = ['']*size
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
        if not((input) in self.glist):
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
                    self.green[i] = char
                else:
                    self.yellow.append(char)
                    self.yellow_index.append(i)
            else:
                if not(char in self.green):
                    self.black.append(char)

    # * For when using website
    #  Parses data from site DOM/shadow DOM
    #
    def web_input(self, input: str):
        # Submit input to the site and add a delay
        enter_word(input)
        time.sleep(2) #! 2 seconds should work, if not: change for an higher value

        # Update program data
        self.inputs.append(input)
        self.try_nb += 1
        nb_correct = 0

        # Retrieve color data from current row from DOM and parse
        row = shadow.find_element("[aria-label='Row "+str(self.try_nb)+"']")
        tiles = shadow.get_child_elements(row)
        for i in range(0, self.size):
            tile = shadow.get_child_elements(tiles[i])[0]
            color = tile.get_attribute("data-state")
            char = input[i]

            if color == "correct":
                self.green[i] = char
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
    #TODO use new_input() if web == 0
    def solve_step(self):
        good1, good2, good3 = False, False, False
        while not(good1 and good2 and good3):
            good1, good2, good3 = True, True, True
            
            if self.try_nb == 0 and self.size == 5:
                word = "adieu"
            else:
                word = self.glist[random.randrange(0, len(self.glist))]

            for j in range(0, self.size):
                char = self.green[j]
                if char != '' and word[j] != char:
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
