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

// const pool = mysql.createPool({
// 	host: "spyder-customer-reviews.cdagscjv6mu0.ap-southeast-1.rds.amazonaws.com",
// 	user:"admin",
// 	password:"Pjy#0618",
// 	database: "spyder"
// })
// gplay.app({appId: appId ,country: country})
// 	.then((body)=>{
// 	    ratings = [appId,country,'googlplay',date, body['reviews'],body['score'],body['ratings'],body['histogram']['1'],body['histogram']['2'],body['histogram']['3'],body['histogram']['4'],body['histogram']['5'] ]
// 	console.log(ratings)
//   pool.getConnection(function(err,con){
//     if (err) {
//       console.log(err);
//     }else{
//       con.query('insert into customer_ratings values(?,?,?,?,?,?,?,?,?,?,?,?)',ratings,function(err, results, fields){
//         if (err) {
//           console.log(err);
//         }
//       })
//     }
//   })
// });

gplay.reviews({
  appId: appId,
  country:country,
	num:200,
  sort: gplay.sort.RATING
}).then((body)=>{
  console.log(body.length)
	// pool.getConnection(function(err,con){
  //   if (err) {
  //     console.log(err);
  //   }else{
	//     for (var i = 0;i<body.length;i++){
  //       reviews = [appId,country,'googlplay',body[i]['date'],body[i]['userName'],body[i]['title'],body[i]['text'],body[i]['score']]
  //       con.query('insert into customer_reviews values(?,?,?,?,?,?,?,?)',reviews,function(err, results, fields){
  //         if (err) {
  //           console.log(err);
  //         }
  //       })
  //     }
  //   }
  // })
})

