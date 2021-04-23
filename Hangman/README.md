# Hangman-game
Simple javascript hangman game that can be run in a terminal.

<br />

## Setup
1. Ensure the files are all in the same folder
2. Change the filePath in line 20 to the path of the folder you stored the files in
3. Run (I am using node.js so I type node CA2.js in the working folder)

<br />

## Other info
1. Using a new wordlist can break the code, the categories are sorted by the indexes of the entries in wordPool.json and you would have to change the category names in the code manually also
2. If you delete all user data to have a fresh game, please leave the code below inside userData.json after deleting everything
```
{
    "table": []
}
```
