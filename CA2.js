/*
    ------------
    HangMan Game
    ------------

    Student ID: p2026086
    Name: Lu Hao Xuan
    Class: DISM/FT/1A03
    Input/Output files: line 21 and 22(respectively)
*/

//Strict coding
'use strict';

//Required modules
var readline = require('readline-sync');
const fs = require('fs');

//Finding the files
const filePath = 'C:\\Users\\ASUS\\OneDrive - Singapore Polytechnic\\SP Year 1-Semester 1\\Fundamentals of programming\\CA2-Assignment';
const fileName = filePath + '/wordPool.json';
const fileName2 = filePath + '/userData.json';

//Declaring variables
var userName, hangManStand, hangManUp1, hangManUp2, hangManUp3, hangManUp4, hangManUp5, hangManUp6, lives,
    wordCount, word, wordArr, poolNumber, wordIndex, correctGuess, userInput, wordObject, lettersArr, lifeLines,
    score, i, j, x, pool, vowelsShown, dateStart, scoreChoice, time, timeTaken, lifeLineArr, passCount, userShown,
    pass, arrCopy, letterIncluded, guessedWord, guessedWordArr, invalidReason, lifeLineChoice;

//Arrays for hangman picture
hangManUp6 = [' ', ' ', ' ', ' '];
hangManUp5 = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '];
hangManUp4 = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '];
hangManUp3 = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '];
hangManUp2 = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '];
hangManUp1 = [' ', '_', '_', '_', ' ', ' ', ' ', ' ', ' '];
hangManStand = '|   |______\n|          |\n|__________|';

//Array for lifeline
lifeLineArr = ['\n(1) Show definition\n', '(2) Show Vowels\n', '(3) Score and pass\n'];

//Initializing variables that need a preset value
wordCount = 1;
lifeLines = 3;
score = 0;
passCount = 0;


//Creating classes

/*
    Word class that contains the word object that contains the name of the word and definition

    Methods:

    1.getWordName - returns the string with the name of the word.

    2.getDefinition - console.log the definition to show the user.

*/
class Word {
    constructor(word, definition) {
        this.word = word;
        this.definition = definition;
    }

    getWordName() {
        return this.word;
    }

    getDefinition() {
        return this.definition;
    }
}


/* 
    WordCollection class with different word pools containing words related to different topics, word pools are 
    arrays with the word objects stored inside.

    Methods:

    1.readFile - Reads the JSON file containing the word pool and returns the data inside the JSON file

    2.getWordObject - Selects a random word from the word pool, removes the word from array after 
    chosen so that same word will not appear again.

    3.checkWord - (Basic requirement)Checks if the word is correctly guessed by user by checking for
    any underscore(_).

    4.checkScore - changes the score based on how many words the user guessed correctly

*/
class WordCollection {
    constructor(wordPool) {
        this.wordPool = wordPool;
    }

    readFile() {
        try {
            //Read contents of the file and store in a variable
            var data = JSON.parse(fs.readFileSync(fileName, 'UTF-8'));
            return data;
        } catch (err) {
            console.error('There was an error when retrieving the file, please check the file and try again...');
        }
    }

    getWordObject() {
        wordIndex = Math.floor(Math.random() * (this.wordPool.length));
        wordObject = this.wordPool[wordIndex];
        this.wordPool.splice(wordIndex, 1);
        return wordObject;
    }

    checkWord() {
        //Presets correctGuess to true
        correctGuess = true;

        //Changes to false if _ is found inside array
        for (i = 0; i < (userShown.length); i++) {
            if (userShown[i] == '_') {
                correctGuess = false;
            }
        }
    }

    checkScore() {
        score = wordCount - 1;
    }
}


//Getting the word pool from JSON file
var JSONWordfile = new WordCollection();
JSONWordfile = JSONWordfile.readFile();

//Creating word object for each key and pushing them into a wordpool array
var fullWordPool = new WordCollection();
var jsPool = new WordCollection();
var geoPool = new WordCollection();
var physicsPool = new WordCollection();
fullWordPool.wordPool = [];
jsPool.wordPool = [];
geoPool.wordPool = [];
physicsPool.wordPool = [];

//Creating the full word pool
for (i = 0; i < 60; i++)
    fullWordPool.wordPool.push(new Word(JSONWordfile[i]["word"], JSONWordfile[i]["definition"]));

//Separating word objects into their specific topics
for (i = 0; i < 20; i++)
    geoPool.wordPool.push(fullWordPool.wordPool[i]);

for (i = 20; i < 40; i++)
    physicsPool.wordPool.push(fullWordPool.wordPool[i]);

for (i = 40; i < 60; i++)
    jsPool.wordPool.push(fullWordPool.wordPool[i]);

//Welcome interface
console.log('\n-= Welcome to Hangman =-\n');

/* 
    Asking for user input to start the game (which topic for words, name)

    Requirements:
    1. User must have entered a name and cannot leave it blank (input is always string so no need for extra steps)

    2. Only contain A-Z, a-z and allow spacing
*/
userName = readline.question('Please enter your username:');

//code here to check if name is valid

while ((userName.length === 0) || invalidName(userName)) {
    console.log('\nInvalid input, your username can only contain alphabets and you must have an username.\n');
    userName = readline.question('Please enter your username:\n');
}

//Letting the user choose what topic he wants for his word
poolNumber = readline.questionInt('\n(1)Javascript\n(2)Physics\n(3)Geography\n(4)Random\nPlease choose a topic:');

while ((poolNumber > 4) || (poolNumber) < 1) {
    console.log('\nInvalid input, you can only enter 1-4.\n');
    poolNumber = readline.questionInt('\n(1)Javascript\n(2)Physics\n(3)Geography\n(4)Random\nPlease choose a topic:');
}

/*
    -----
    Timer
    -----
    -Gets the date at the start of the game and end of the game, the difference is the 
    time passed in milliseconds which can be converted to seconds and minutes to be
    clearer
*/
dateStart = new Date();

/*
------------------------------------------------------------------------------------------------------------------------
    Main program

    -Program ends when user correctly correctGuesses 10 words or correctGuessed a wrong letter 9 secondss(9 lives total)
------------------------------------------------------------------------------------------------------------------------
*/
do {
    //Getting a new word object by finding the pool and using the getWordObject method
    findPool(poolNumber);
    wordObject = pool.getWordObject();

    //Getting the name of the word from the word object
    word = wordObject.getWordName();

    //Converting the name of the word to a string
    wordArr = word.split('');

    //Resets correctGuessed letters and userShown after each run
    lettersArr = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
        'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
        'V', 'W', 'X', 'Y', 'Z'];
    userShown = [];

    //Resets hangman picture
    hangManUp6 = [' ', ' ', ' ', ' '];
    hangManUp5 = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '];
    hangManUp4 = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '];
    hangManUp3 = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '];
    hangManUp2 = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '];
    hangManUp1 = [' ', '_', '_', '_', ' ', ' ', ' ', ' ', ' '];
    hangManStand = '|   |______\n|          |\n|__________|';

    //Resets some values after each cycle when user correctly guesses the word
    correctGuess = false;
    pass = false;
    lives = 9;

    //Adding _ for the length of the word 
    for (i = 0; i < word.length; i++) {
        userShown.push('_');
    }

    //Shows word count
    console.log('\nWord ' + wordCount + ' / 10');

    /*
        -------------------------------------
        Program for until the word is guessed 

        -Program ends when user passes, word is correctly guessed, user has run out of lives
        -------------------------------------
    */
    do {

        //Prints all the _ for length of the word
        printSpace(userShown);

        //Prints all the letters that have not been guessed
        printSpace(lettersArr);

        //Asks for input and changes it to uppercase
        userInput = readline.question('(1) to use lifelines\n(2) to guess the entire word\n(3) to pass\n' + userName + '\'s guess:');
        userInput = userInput.toUpperCase();

        /* 
            Checks if input is valid and execute the above again if it is invalid

            Conditions:
            1. Only can be a lowercase or uppercase Letter (No special characters)
            2. Only 1 character (Checks if nothing or more characters are entered)
            3. Cannot be any other number other than the numbers used for the program (0, 9, 8)
            4. Letters cannot be guessed twice
        */
        while (invalidInput(userInput)) {
            console.log('\nInvalid input, ' + invalidReason + '\n');
            printSpace(userShown);
            printSpace(lettersArr);
            userInput = readline.question('(1) to use lifelines\n(2) to guess the entire word\n(3) to pass\n' + userName + '\'s guess:');
            userInput = userInput.toUpperCase();
        }

        if (userInput == 1) {

            /*
                -------------------------------------------
                Section if the user chooses to use lifeline
                -------------------------------------------
            */
            if (lifeLines > 0) {

                //Ask user which lifeline he wants
                lifeLineChoice = readline.questionInt(lifeLineArr.join('') + '(4) to exit lifeline\nChoose lifeline:');

                //Validation for above
                while ((lifeLineChoice != 1) && (lifeLineChoice != 2) && (lifeLineChoice != 3) && (lifeLineChoice != 4)) {
                    console.log('Invalid input, only lifelines 1-3 can be selected or 4 to exit lifeline.');
                    lifeLineChoice = readline.questionInt(lifeLineArr.join('') + '(4) to exit lifeline\nChoose lifeline:');
                }

                //Checks if user already used the lifeline
                if (lifeLineArr[lifeLineChoice - 1] === '\n') {
                    console.log('\nYou already chose this lifeline.\n');

                } else {

                    //Uses the lifeline and the user can no longer use it
                    switch (lifeLineChoice) {
                        case 1: console.log('\n' + wordObject.getDefinition() + '\n');
                            lifeLines--;
                            lifeLineArr[0] = '\n';
                            break;
                        case 2: getVowels();
                            if (vowelsShown == false) {
                                lifeLineArr[1] = '\n';
                                lifeLines--;
                                //Check if word is completed after showing vowels
                                pool.checkWord();
                                break;
                            } else {
                                console.log('\nAll vowels are showned.\n');
                            }
                            break;
                        case 3: correctGuess = true;
                            console.log('\nThe word was ' + word);
                            lifeLines--;
                            lifeLineArr[2] = '\n';
                            break;
                        default: console.log('\nExiting lifeline...');
                    }

                }

            } else {

                //If user ran out of lifelines
                console.log('\nYou have ran out of lifelines.\n');
            }

        } else if (userInput == 2) {

            /* 
                ---------------------------------------------
                Section if user attempts to guess entire word
                ---------------------------------------------
            */

            //Asks user to input the word, sets all the characters to uppercase and splits the string into an array
            guessedWord = readline.question('Guess the word:');
            guessedWord = guessedWord.toUpperCase();
            guessedWordArr = guessedWord.split('');

            //Checks if the input is valid
            while (invalidWordInput(guessedWordArr)) {
                console.log('Invalid input, ' + invalidReason);
                guessedWord = readline.question('Guess the word:');
                guessedWord = guessedWord.toUpperCase();
                guessedWordArr = guessedWord.split('');
            }

            //Checks if both the word array and guessed word array are of same length then moves on to second check
            if (guessedWordArr.length === wordArr.length) {

                //Presets correctGuess to true
                correctGuess = true;

                //Checks if there is any different letters and sets correctGuess to false if there are any
                for (i = 0; i < wordArr.length; i++) {
                    if (guessedWordArr[i] != wordArr[i])
                        correctGuess = false;
                }

                //if correctGuess is false, it will tell the user and minus a life
                if (correctGuess == false) {
                    console.log('\nWrong word ' + userName);
                    lives--;
                    printHangMan(lives);
                }

                //Straight away executes wrong word and minus life if the two word arrays are of different length
            } else {
                console.log('\nWrong word ' + userName);
                lives--;
                printHangMan(lives);
            }

        } else if (userInput == 3) {
            /*
                ---------------------------------------
                Section for if the user chooses to pass
                ---------------------------------------

                -Only allows user to pass if he/she has 9 lives as if there is no requirement user can
                just pass whenever he/she has 1 life left
            */
            if (lives === 9) {
                //Checks if the user has passed more than 10 times and decides whether the user can pass
                if (passCount < 10) {
                    pass = true;
                    passCount++;
                    console.log('\nWord passed... You have ' + (10 - passCount) + ' passes left.');
                } else {
                    console.log('\nYou have ran out of passes.');
                }
            } else {
                console.log('\nYou can only pass if you have 9 lives.');
            }


        } else {
            /* 
                -----------------------------------------------------
                Section to check if letter guessed is inside the word
                -----------------------------------------------------
            */

            //Presets letterIncluded to false
            letterIncluded = false;

            //Checks if the userInput is inside the word and changes letterIncluded to true if it is inside
            for (i = 0; i < (userShown.length); i++) {
                if (wordArr[i] == userInput) {
                    userShown[i] = userInput;
                    letterIncluded = true;
                }
            }

            //Prints different messages depending if the letter is correct or wrong
            if (letterIncluded === false) {
                lives--;
                console.log('\nSorry ' + userInput + ' is not part of the word.\n');
                printHangMan(lives);
            } else {
                console.log('\nGood job! ' + userInput + ' is one of the letters.\n');
            }

            //Final check to see if word has been completed
            pool.checkWord();
        }

    } while ((correctGuess != true) && (lives > 0) && (pass == false));

    //Checks if sub program ended if its because the word is guessed and not because it was passed
    if (correctGuess === true) {
        wordCount++;
        console.log('\nYou have correctly guessed the word');
    }

    //Changes the score depending on the word count
    pool.checkScore();
} while ((wordCount <= 10) && (lives > 0));


//Congratulations message if user manages to guess all 10 words
if (wordCount === 11) {
    console.log('Congratulations you won, please give me A.');
}


//Ends timer and gets time passed in milliseconds
timeTaken = new Date() - dateStart; // time elapsed in milliseconds
time = millisToMinutesAndSeconds(timeTaken);

//Tells the user his/her stats
console.log('\nName:' + userName + ' Score:' + score + ' Time elapsed:' + time + '\n');


/*
    userData class to write/read/show the score of the players

    Methods:

    1.readFile - read the file and creates a table if there is none, if there is a table
    simply reads the file

    2.writeFile - write the user data into the JSON file

    3.showScoreBoard - shows the score board and is sorted by score and fastest time if they have the
    same score

    4.showStats - show the users highest, lowest and average score

*/
class userData {

    constructor(userName, score, time) {
        this.userName = userName;
        this.score = score;
        this.time = time;
    }

    readFile() {
        try {
            //Read contents of the file and store in a variable
            var data = fs.readFileSync(fileName2, 'UTF-8');

            //Create table if there is none
            if (!data) {
                data = {
                    table: []
                }
            } else {
                data = JSON.parse(fs.readFileSync(fileName2, 'UTF-8'));
            }
        } catch (err) {
            console.error('There was an error when retrieving the file, please check the file and try again...');
        }
        return data;
    }

    writeFile() {
        var data = this.readFile();
        var userData = {
            score: this.score,
            userName: this.userName,
            time: this.time
        }
        data.table.push(userData);

        try {
            //Read contents of the file and store in a variable
            fs.writeFileSync(fileName2, JSON.stringify(data));
        } catch (err) {
            console.error('There was an error when retrieving the file, please check the file and try again...');
        }
    }

    showScoreBoard() {
        //Read the file with user data and push into array
        var userData = this.readFile();
        var dataArray = [];
        for (i = 0; i < userData.table.length; i++)
            dataArray.push(userData.table[i]);

        //Sorts the scoreboard
        var sortedArr = dataArray.sort((a, b) => a.score < b.score ? 1 : a.score > b.score ? -1 : a.time > b.time ? 1 : a.time < b.time ? -1 : 0);

        //Prints the score board
        console.log('\nScoreboard:\n');
        // console.table('Name:' + sortedArr[i]["userName"] + 'Score:' + sortedArr[i]["score"] + 'Time elapsed:' + sortedArr[i]["time"]);
        console.table(sortedArr);
    }

    showStats(userName) {
        //Read the file with user data and push into array
        var userData = this.readFile();
        var dataArray = [];
        var scoreArr = [];
        for (i = 0; i < userData.table.length; i++)
            dataArray.push(userData.table[i]);

        //Finds all the scores of the user and store into array
        for (i = 0; i < dataArray.length; i++) {
            if (dataArray[i]["userName"] == userName) {
                scoreArr.push(dataArray[i]["score"]);
            }
        }

        //Add up all the scores and find the average
        var average = 0;
        for (i = 0; i < scoreArr.length; i++) {
            average += scoreArr[i];
        }
        average /= scoreArr.length;

        //Sort array from lowest to highest
        scoreArr.sort((a, b) => a - b);

        //Prints the statistics to user
        console.log('\nAverage score:' + average.toFixed(2));
        console.log('Highest score:' + scoreArr[scoreArr.length - 1]);
        console.log('Lowest score:' + scoreArr[0] + '\n');
    }
}


//Create object player to store the stats and write them into the file
var player = new userData(userName, score, time);
player.writeFile();

//Ask user if he wants to see any statistics
scoreChoice = readline.question('(1) Show scoreboard\n(2) Show user statistics\n(3) Exit game\nPlease choose:');

//Validation for above
while ((scoreChoice) != 1 && (scoreChoice != 2) && (scoreChoice != 3)) {
    console.log('\nInvalid input, only choose 1 or 2 or 3.\n');
    scoreChoice = readline.question('(1) Show scoreboard\n(2) Show user statistics\n(3) Exit game\nPlease choose:');
}

//Shows the user what he selected
if (scoreChoice == 1)
    player.showScoreBoard();
else if (scoreChoice == 2)
    player.showStats(userName);
else
    console.log('Exiting game, thanks for playing...');


/*
    ---------
    Functions
    ---------
*/


/*  
    -------------------------
    Function to find the pool
    -------------------------
*/
function findPool(poolNumber) {
    if (poolNumber === 4)
        pool = fullWordPool;
    else if (poolNumber === 3)
        pool = geoPool;
    else if (poolNumber === 2)
        pool = physicsPool;
    else
        pool = jsPool;
}


/*  
    -----------------------------------------------------------
    Function to print the hang man based on how many lives left
    -----------------------------------------------------------
*/
function printHangMan(lives) {
    //Switch statement to mutate arrays when the user correctGuesses a wrong letter
    switch (lives) {
        case 8: hangManUp1.splice(2, 1, '|');
            hangManUp2.splice(2, 1, '|');
            hangManUp3.splice(2, 1, '|');
            hangManUp4.splice(2, 1, '|');
            hangManUp5.splice(2, 1, '|');
            hangManUp6.splice(3, 1, '_____');
            break;
        case 7: hangManUp5.splice(7, 1, '|');
            break;
        case 6: hangManUp4.splice(7, 1, 'o');
            break;
        case 5: hangManUp3.splice(7, 1, '|');
            break;
        case 4: hangManUp3.splice(6, 1, '/');
            break;
        case 3: hangManUp3.splice(8, 1, '\\');
            break;
        case 2: hangManUp2.splice(7, 1, '|');
            break;
        case 1: hangManUp1.splice(6, 1, '/');
            break;
        case 0: hangManUp1.splice(8, 1, '\\');
            hangManStand += '\nGame Over, you ran out of lives.';
    }

    //console log to print the hangman picture
    console.log(hangManUp6.join('') + '\n' + hangManUp5.join('') + '\n' +
        hangManUp4.join('') + '\n' + hangManUp3.join('') + '\n' +
        hangManUp2.join('') + '\n' + hangManUp1.join('') + '\n' +
        hangManStand);
}



/*
    ----------------------------------------------------
    Function to print the array in a string with spacing
    ----------------------------------------------------

    -.slice() is used to make a copy of the array as if i do not make a copy the elements in the
      original array will also have the space added and mess up the program.
*/
function printSpace(arr) {
    //Makes copy of array
    arrCopy = arr.slice('');

    //Adds spacing to every element in array
    for (i = 0; i < arrCopy.length; i++) {
        arrCopy[i] += ' ';
    }

    //Prints the result
    console.log('\n' + arrCopy.join('') + '\n');
}


//Function to show vowels
function getVowels() {
    //Vowels array to contain the vowels declared locally as i do not need it outside
    var vowelsArr = ['A', 'E', 'I', 'O', 'U'];

    /*
    Boolean to tell me if all vowels are already shown if true 
    it will tell user and not take away the lifeline 
    */
    vowelsShown = true;

    //Loop to check if word contained vowels and changes the value to the vowel if there is one
    for (i = 0; i < vowelsArr.length; i++) {

        //Changes different vowels to check
        var vowelCheck = vowelsArr[i];

        //If word contains vowel it will replace it
        for (x = 0; x < userShown.length; x++) {
            if (wordArr[x] === vowelCheck) {
                userShown[x] = vowelCheck;

                //Remove letters from letters array if vowels are found so users does not see it
                for (j = 0; j < lettersArr.length; j++) {
                    if (lettersArr[j] == vowelCheck) {
                        lettersArr.splice(j, 1, ' ');
                        vowelsShown = false;
                    }
                }
            }
        }
    }
}


/* 
    -----------------------------------
    Functions for validation for Inputs 
    -----------------------------------
    My while loop for validation is while (invalidInput(userInput)) because if there is an invalid input 
    detected the function will return a string and a string is a truthy value hence the loop will run
    i did not use boolean values
*/

/*
    -------------------
    Validation for name
    -------------------
*/
function invalidName(userName) {
    return !/^[a-zA-Z ]+$/.test(userName);
}


/*
    -----------------------------------------------------
    Validation for word input if user guessed entire word
    -----------------------------------------------------
*/
function invalidWordInput(guessedWordArr) {
    //Checks if it is empty input
    if (guessedWordArr.length == 0)
        return invalidReason = 'You must at least enter 1 letter in your word.';

    //Checks for special characters 
    for (i = 0; i < guessedWordArr.length; i++) {
        if (/[\s~`!@#$%\^&*+=\-\[\]\\';,/{}|\\":<>\?()\._]/g.test(guessedWordArr[i]))
            return invalidReason = 'word includes a special character.';
    }

    //Checks for numbers
    for (i = 0; i < guessedWordArr.length; i++) {
        if (!isNaN(guessedWordArr[i]))
            return invalidReason = 'word includes a number';
    }
}


/* 
    ---------------------------
    Validation for letter input
    ---------------------------
*/
function invalidInput(userInput) {
    //Checks for special characters 
    if (/[\s~`!@#$%\^&*+=\-\[\]\\';,/{}|\\":<>\?()\._]/g.test(userInput)) {
        return invalidReason = 'you have entered a special character.';

        //Checks if user input 0 or more characters than 1

    } else if (userInput.length != 1) {
        return invalidReason = 'you can only enter 1 letter.';

        //Checks if user entered any number other than the choices
    } else if (!isNaN(userInput)) {
        if ((userInput != 1) && (userInput != 2) && (userInput != 3))
            return invalidReason = 'you can only choose a number related to the choices given.';

        //Checks if letter is already guessed
    } else {

        //Presets alreadyGuessed to true
        var alreadyGuessed = true;

        //Changes alreadyGueseed to false if letter is found in letter array and takes it out from letter array
        for (i = 0; i < lettersArr.length; i++) {
            if (userInput == lettersArr[i]) {
                lettersArr.splice(i, 1, ' ');
                alreadyGuessed = false;
            }
        }

        //If letter is already guessed 
        if (alreadyGuessed == true)
            return invalidReason = 'you have already guessed this letter.';
    }
}


/*  
    ----------------------------------------------------------
    Function for converting milliseconds to more readable time
    ----------------------------------------------------------
*/
function millisToMinutesAndSeconds(millis) {
    var minutes = Math.floor(millis / 60000);
    var seconds = ((millis % 60000) / 1000).toFixed(0);
    return (seconds == 60 ? (minutes + 1) + ':00' : minutes + ':' + (seconds < 10 ? '0' : '') + seconds);
}