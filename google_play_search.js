var gplay = require('google-play-scraper');

term='명일방주'
country = 'kr'

gplay.search({
    term: term,
    num: 2,
    country: country
  }).then(console.log, console.log);
