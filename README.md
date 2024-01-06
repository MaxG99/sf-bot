Runs with python 3.10

Install tesseract:
[https://github.com/tesseract-ocr/tesstrain](https://github.com/UB-Mannheim/tesseract/wiki)https://github.com/UB-Mannheim/tesseract/wiki

change path to tesseract in the main.py file to the corresponding file

change username and password  (currently hardcoded in script)
-> run the bot.

The bot currently chooses the best quest ep/time and starts the adventure
Items are not considered yet.

Note: sometimes the xp per quest are not read correctly (one additional number at the start), to mitigate the problem a correction solution was built that truncates that first number
it could result in an uncorrect reading from time to time but ist much better than without.

In the future I plan to train my own tesseract model to get better reading.

TODO:
consider items
automatically fight dungeons and arena
guild fights
fortress

