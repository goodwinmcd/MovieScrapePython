These files are used to obtain information on movies with a given title.  The individual functions can 
be used to obtain specific information or the the getMoveInfo() function can be used to obtain all the 
data automatically.  

Challenges that were come across and the solutions.
  Problem: Foreign characters for foreign movie titles and parsing them to regular characters so that the
  seach results would be consistent.
  Solution:  Found a library called unidecode that would convert the characters to unicode.  Application can 
  be seen on line 26 of movieScrape.py

  Problem: I collected a list of movies to collect data for from rotten tomatos, IMDB, and metacritic.  Rotten tomatos includes foreign
  title and english title of foreign films.  Imdb only includes the english title.  This was allowing duplicates 
  to enter the database because my program would see a movie title collected from a rotten tomatoes list as a different movie from 
  a movie title collected from IMDB even though they were the same movie.  
  Solution:  I query the database to pull up any movie that might contain the english title (since metacritic, rotten 
  tomatos, and IMDB all include the english title) using wild card characters.  If the query returns a result then I
  do not upload the movie.  

  Problem: Rotten tomatoes uses javascript to generate dynamic HTML for their search results.  This means I couldn't retrieve search
  results from rotten tomatoes without generating the HTML first.  
  Solution: I used a python library called selenium that opens a browser to the requested URL, waits for it to load, and then retrieves
  the HTML.  Once the HTML is retrieved it closes the browser.  

  Problem:  If anything that is loaded on a browser page using selenium returns a 404 (such as an ad) then selenium will close and 
  the program will crash. If I am collecting information on 2000 movies and this happens on the 54th movie and I am not around to 
  restart it then that is a lot of wasted time.  
  Solution:  I used a linux bash script to repeatedly call the program in a never ending while loop.  If the program crashes it is 
  immediatly restarted.  

  Problem:  Inconsistency between dates between rotten tomatoes and imdb (usually off by a year).  
  Solution:  The release date of a movie is always obtained from imdb.  It then compares that date +/- 1 when searching rotten tomatoes
  for a certain title.  

Future work to do:
  Use Imdbs advance search so that TV shows and date range are covered through searching IMDB instead of error checking in the program.  
  Find more consistent methods of finding runtime and meta ratings.

Please feel free to contact me with any questions. 
