# YORDLE 
Simple [Wordle](https://www.powerlanguage.co.uk/wordle/) solver using Selenium for Python3



## Dependencies
- Selenium (_pip install selenium_) and corresponding webdriver, geckowebdriver by default  
- pyshadow (_pip install pyshadow_) because Wordle website uses shadowDOM a LOT

## How to use
Simply execute yordle.py. Program might not always find the hidden word, but has shown to be quite reliable in my experience.

## How it works
This **isn't** an AI by any means: the program takes random words from a list (gathered from website source code) and checks if they meet requirements with known data at a said stage of a game.  
It then repeats this behaviour until it finds the right word :) or fails to do so in less than 6 tries :(

## Example
https://user-images.githubusercontent.com/79169411/150977579-ee492f9b-1d10-4871-9afe-f87ef0725940.mp4
