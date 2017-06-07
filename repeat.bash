#!/bin/bash
while true
do
  python imdbScrape.py
  pkill -f firefox
done
