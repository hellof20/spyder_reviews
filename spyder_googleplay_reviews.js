var gplay = require('google-play-scraper');
const mysql = require('mysql')

Date.prototype.Format = function(fmt) { //author: meizz
    var o = {
        "M+": this.getMonth() + 1, //月份
        "d+": this.getDate(), //日
        "h+": this.getHours(), //小时
        "m+": this.getMinutes(), //分
        "s+": this.getSeconds(), //秒
        "S": this.getMilliseconds() //毫秒
    };
    if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
    for (var k in o)
        if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
    return fmt;
}
/*
gplay.search({
    term: "Arknights",
    num: 2,
    country: 'jp'
  }).then(console.log, console.log);
*/

appId = 'com.YoStarJP.Arknights'
country = 'jp'
var date = new Date().Format("yyyy-MM-dd hh:mm:ss")

var connection = mysql.createConnection({
	host: "spyder-customer-reviews.cdagscjv6mu0.ap-southeast-1.rds.amazonaws.com",
	user:"admin",
	password:"Pjy#0618",
	database: "spyder"
});

gplay.reviews({appId: appId, num:200000,sort: gplay.sort.RATING}).then((body)=>{
	reviewsdata = body;
   reviewsnum = body.length;
  console.log(reviewsnum);
  gplay.app({appId: appId})
  .then((body)=>{
    ratings = [appId,country,'googlplay',date, reviewsnum, body['score'],body['ratings'],body['histogram']['1'],body['histogram']['2'],body['histogram']['3'],body['histogram']['4'],body['histogram']['5'] ]
    console.log(ratings)
    connection.query('insert into customer_ratings values(?,?,?,?,?,?,?,?,?,?,?,?)',ratings,function(err, results){
      if(err){console.log(err)}
      else{
        connection.query('delete from customer_reviews where appid = "'+ appId + '"',function(err,results){
          if(err){console.log(err)}
          else{
		              var reviews = [];
            for (var i = 0;i<reviewsnum;i++){
              reviews.push({'appid':appId,'country':country,'platform':'googlplay','date':reviewsdata[i]['date'],'name':reviewsdata[i]['userName'],'title':reviewsdata[i]['title'],'content':reviewsdata[i]['text'],'rating':reviewsdata[i]['score']})
            }
            connection.query('insert into customer_reviews set ?',reviews,function(err, results){
              if (err) {console.log(err)}
              connection.end()
            })
          }
        })
      }
    })
  })
})
