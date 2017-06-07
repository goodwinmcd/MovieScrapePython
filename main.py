#!/usr/bin/env

#This program uses the movieScrape.py functions to retrieve info on rotten tomatos and metacritics 
#top 100 movies from the years 1997 to 2017 (the past 20 years) and uploads them to my database

from movieScrape import *

movieSearch = []
year = '2016'
for i in range(0, 20):
  print(i)
  url = 'http://www.metacritic.com/browse/movies/score/metascore/year/filtered?year_selected=' + str(year) + '&sort=desc'
  rtUrl = 'https://www.rottentomatoes.com/top/bestofrt/?year=' + str(year)
  getRTList(rtUrl, movieSearch)
  getMetaList(url, movieSearch)
  year = int(year) - 1
getimdbList('http://www.imdb.com/chart/top?ref_=nv_mv_250_6', movieSearch)
getRTList('https://www.rottentomatoes.com/top/bestofrt/', movieSearch)

db = MySQLdb.connect('localhost','root','Ranford1', 'movieList')
c = db.cursor()
errors = open('moviesNotLoaded.txt', 'w')

movieSet = set(movieSearch)
print(len(movieSet))
for i, each in enumerate(movieSet):
  print(each)
  print(i)
  c.execute("""SELECT title, date FROM movieList.movie WHERE title=%s AND date=%s""", (each[:-7], each[-5:-1],))
  r = c.fetchall()
  if len(r) == 0:
    movie = getMovieInfo(each)
    if movie == None: errors.write(each + '\n')
    else:
      movie['Title'] = movie['Title'][:-7]
      uploadMovie(movie, c)
      db.commit()
errors.close()
