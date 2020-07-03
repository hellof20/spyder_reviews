var gplay = require('google-play-scraper');

term = 'Azur Lane'
country = 'jp'

gplay.search({
    term: term,
    num: 2,
    country: country
  }).then(console.log, console.log);
