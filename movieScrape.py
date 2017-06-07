#This program defines functions that can be used to collect data on a movie from a 
#given title and date.  The information is collected from imdb and also provides functions
#to retrieve the rotten tomato score and imdb score

#!/usr/bin/env

import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from unidecode import unidecode
import time
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb

#This function retrieves a movies url on IMDB using a title and a date passed in the format of title (date)
def getIMDBURL(title):
  #Search movie title combined with the movies release year and select
  #first option
  title = title.replace(' ', '+')
  date = title[-5:-1]
  if date == '(TBA': return None
  url = "http://www.imdb.com/find?ref_=nv_sr_fn&q=" + title + '&s=tt&exact=true&ref_=fn_al_tt_ex'
  url = unidecode(url)                                  #For foreign characters in movie title
  page = urlopen(url)
  soup = BeautifulSoup(page, "html.parser")
  result = soup.find('td', class_ = 'result_text')
  if result == None: return None
  movieLink = 'http://www.imdb.com'+ result.a['href']	
  return movieLink

#Function to collect all movie information
#of a movie from imdb at once
def getMovieInfo(title):
  movieLink = getIMDBURL(title)
  if movieLink == None: return None
  #load movie result page
  page = urlopen(movieLink)
  soup = BeautifulSoup(page, "html.parser")
  runtime = getRuntime(soup)                            #call runtime function to get runtime
  rtRating = getRTRating(title.replace('+', ' '))       #call rtRating function to get rotten tomatos rating
  genre = getGenres(soup)                               #call genre function to get array of genres
  imdbRating = getImdbRating(soup)                      #call imdbRating function to get array of imdb rating
  metaRating = getMetaRating(soup)                      #call getMetaRating function to get meta critic rating from imdb page   
  budget = getBudget(soup)                              #get budget
  gross = getRevenue(soup)                              #get revenue
  #Insert all info into a dictionary
  movieInfo = {'Title': title.replace('+', ' '), 'Date': date, 'Length': runtime, 'Genres': genre, 'imdbRating': imdbRating, 'metaRating': metaRating, 'rtRating': rtRating, 'Budget': budget, 'Gross': gross,}
  return movieInfo

#A function to upload a movie to my database
def uploadMovie(movie, c):
  #This checks to see if a movie is already in the database.  It checks date and title so remakes will still be allowed to be uploaded
  c.execute("""SELECT title, date FROM movie WHERE title=%s""", (movie['Title'],))
  r = c.fetchall()
  upload = True
  for each in r:
    if (each[0] == movie['Title']) & ((each[1] == movie['Date']) | (each[1] == str(int(movie['Date']) - 1)) | (each[1] == str(int(movie['Date']) + 1))):
      upload = False
  #RT includes foreign film name and english title.  This causes duplicates in the DB.  This test to make sure 
  #there is not already a foreign film in the DB
  c.execute("""SELECT title, date FROM movie WHERE title LIKE %%s%""", (movie['Title'],))
  for each in r:
    if (movie['Title'] in each[0]) and (movie['Date'] == each[1]): upload = False
  #upload movie info into movie table
  if upload == True:
    c.execute("""INSERT INTO movie (title, date, runtime, budget, gross, imdb, rt, meta) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""", (movie['Title'], movie['Date'], movie['Length'], movie['Budget'], movie['Gross'], movie['imdbRating'], movie['rtRating'], movie['metaRating']))
    genreid = []
    #upload genres and match the corresponding genre to the correct movie id in the link table
    for each in movie['Genres']:
      c.execute("""SELECT id, descript FROM genre WHERE descript=%s;""", each)
      r = c.fetchall()
      if len(r) == 0:
        c.execute("""INSERT INTO genre (descript) VALUES (%s);""", (each,))
        c.execute("""SELECT * FROM genre WHERE descript=%s;""", (each,))
        r = c.fetchall()
        genreid.append(r[0][0])
      else:
        genreid.append(r[0][0])
    c.execute("""SELECT id, title FROM movie WHERE title=%s""", (movie['Title'],))
    r = c.fetchall()
    movieId = r[0][0]
    for each in genreid:
      c.execute("""INSERT INTO moviegenre (movieid, genreid) VALUES (%s, %s);""", (movieId, each,))

def getBudget(soup):
  budget = soup.find('h4', text = 'Budget:')
  if budget != None:
    budget = budget.parent.contents[2].strip()
    budget = budget.replace(',','')[1:]
    budget = list(filter(str.isdigit, budget))
    budget = int(''.join(budget))
    return budget
  else: return None

def getRevenue(soup):
  gross = soup.find('h4', text = 'Gross:')
  if gross != None:
    gross = gross.parent.contents[2].strip()
    gross = gross.replace(',','')[1:]
    return int(gross)
  else: return None

def getMetaRating(soup):
  metaRating = soup.find('div', class_ = 'titleReviewBar')
  if metaRating != None:
    metaRating = metaRating.find('span').contents[0]
    if metaRating == '\n': metaRating = None
    else: metaRating = int(metaRating)
  return metaRating

def getImdbRating(soup):
  imdbRating = soup.find('span', class_ = 'rating')
  if imdbRating != None: imdbRating = int(float(imdbRating.contents[0])*10)
  return imdbRating

def getGenres(soup):
  genre = soup.find_all('span', itemprop='genre')
  if genre != None:
    for i,each in enumerate(genre):
      genre[i] = genre[i].contents[0]
  return genre

def getRuntime(soup):
  runtime = soup.find('h4', text='Runtime:')
  if runtime != None:
    runtime = runtime.parent.time.contents[0]
    runtime = int(runtime.partition(' ')[0])
  if runtime == None:
    runtime = soup.find('time', itemprop = 'duration')
    if runtime != None:
      runtime = runtime['datetime']
      runtime = runtime[2:-1]
  return runtime

#RT rating was challenging because the raw html did not contain the data.  The data I needed was generated by javascript
#after the page was loaded
def getRTRating(title):
  date = title[-5:-1]
  title = title[:-6]
  title.replace(' ', '%20')
  binary = FirefoxBinary('/usr/lib/firefox/firefox')
  browser = webdriver.Firefox(firefox_binary = binary)
  url = 'https://www.rottentomatoes.com/search/?search=' + title
  browser.get(url)
  html = browser.page_source
  time.sleep(1)
  browser.quit()
  soup = BeautifulSoup(html, 'html.parser')
  results = soup.find('section', id = 'movieSection')
  if results == None: return 0
  results = results.find_all('div', class_ = 'details')
  if results == None: return 0
  #Search all returned movies on the page and only return the information if the date and title match
  for each in results:
    searchTitle = each.a.contents[0]
    if searchTitle == None: return 0
    searchDate = each.find('span', class_ = 'movie_year')
    if searchDate == None: return 0
    searchDate = searchDate.contents[4]
    title = title.replace('%20', ' ')
    title = title.strip()
    print(searchTitle)
    if ((str(searchDate) == date) or (str(searchDate) == str(int(date) -1)) or (str(searchDate) == str(int(date) + 1))) and ((searchTitle.lower()) == title.lower() or (title in searchTitle)):
      rating = each.parent
      rating = rating.find('span', class_ = 'tMeterScore')
      if rating == None: return 0
      rating = rating.contents[1]
      return int(rating)
      break

#A function that collects all movie titles and dates on any specific list of imdb (like top horror movies)
def getimdbList(url, movieList):
  page = urlopen(url)
  soup = BeautifulSoup(page, "html.parser")
  titles = soup.find_all('td', class_ = 'titleColumn', limit = 100)
  dates = soup.find_all('span', class_ = 'secondaryInfo', limit = 100)
  movieList = []
  for i, movies in enumerate(titles):
    title = movies.a.contents[0]
    date = str(dates[i].contents[0])
    title = title + " " + date
    movieList.append(title)

#A function that gets all movie titles and dates from any given RT list (like top 100 movies of 2016)
def getRTList(url, movieList):
  page = urlopen(url)
  soup = BeautifulSoup(page, 'html.parser')
  titles = soup.find('table', class_ = 'table')
  titles = titles.find_all('a')
  for i, movies in enumerate(titles):
    title = str(movies.contents[0])
    title = title.strip()
    movieList.append(title)

#A function that gets all movie titles and dates from any given metacritic list (like top thrillers of all time)
def getMetaList(url, movieList):
  req = urllib.request.Request(url, headers={'User-Agent' : "Magic Browser"})
  page = urllib.request.urlopen(req)
  soup = BeautifulSoup(page, 'html.parser')
  titles = soup.find_all('div', class_ = 'title')
  dates = soup.find_all('td', class_ = 'date_wrapper')
  for i, movies in enumerate(titles):
    title = movies.a.contents[0]
    date = dates[i].span.contents[0]
    date = date.split(" ")
    date = date[len(date) - 1]
    date = "(" + date + ")"
    title = title + " " + date
    movieList.append(title)
