Runs with python 3.10

Install tesseract:
[https://github.com/tesseract-ocr/tesstrain](https://github.com/UB-Mannheim/tesseract/wiki)https://github.com/UB-Mannheim/tesseract/wiki

➡️change path to tesseract in the main.py file to the corresponding file

➡️change username and password  (currently hardcoded in script)

➡️in order to prevent the bot from choosing a wrong quest at the first run edit the value_ref.txt and insert you current exp/second value of any quest
➡️ run the bot.

The bot currently chooses the best quest ep/time and starts the adventure
Items are not considered yet.

!! Bot stops if there is no alu left so if you want to play >100 you have to drink manually and restart the bot

Note: sometimes the xp per quest are not read correctly (one additional number at the start), to mitigate the problem a correction solution was built that truncates that first number
it could result in an uncorrect reading from time to time but ist much better than without.

In the future I plan to train my own tesseract model to get better reading.

TODO:
consider items
automatically fight dungeons and arena
guild fights
fortress

