const express = require('express'),
    rp = require('request-promise'),
    P = require('bluebird'),
    Twitter = require('twitter'),
    Json2csvParser = require('json2csv').Parser;

const app = express()

const CONSUMER_KEY = 'ftVp1RSJdhUcfnZyY2i3O1bZa',
CONSUMER_SECRET = 'IQZE5HJz0RvDSKJL9vWm4MxyLeo4uUNRqlH1c0sNXsSVR9J1Hi',
OAUTH_TOKEN = '900054427251294209-yLexnISGAhLNvKq2lanqJV0rQhRy6YO',
ACCESS_TOKEN_SECRET = 'tl5gZLDx5SYW8mu1JMzplk8T2VAi9xK88PrKy2EWFepid'
 
const client = new Twitter({
    consumer_key: CONSUMER_KEY,
    consumer_secret: CONSUMER_SECRET,
    access_token_key: OAUTH_TOKEN,
    access_token_secret: ACCESS_TOKEN_SECRET
  });

app.use(function(req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-  With, Content-Type, Accept");
    next();   
});
 
app.get('/crypto/trends', (req, res) => {

let twitterData = [];

    client.get('search/tweets', {
        q: req.query.keyword,
        lang: 'en',
        count: 15,
        result_type:'popular',
        tweet_mode: 'extended'
    }).then((data) => {
        data.statuses.forEach((tweetData) =>{
            twitterData.push(
                {
                user_id: tweetData.user.id,
                twitter_handle: tweetData.user.screen_name,
                user_name: tweetData.user.name,
                tweet_id: tweetData.id,
                popular_tweet_content: tweetData.full_text,
                followers_count: tweetData.user.followers_count,
                retweet_count: tweetData.retweet_count || 0,
                likes_count: tweetData.favorite_count || 0
            })
        })
        return P.all(twitterData);
    }).then((userTweetData) => {
        let filterStatus= [];
        userTweetData.forEach((data)=>{
            filterStatus.push(getTweets(data));
        })
        return P.all(filterStatus);
    }).then(()=> {
        twitterData.forEach((data)=>{
            const filterValue = twitterData.filter((filterData)=>{
                if(filterData.user_id == data.user_id)
                return filterData;
            });
            data.trend_factor = filterValue.length;
        })
        return P.resolve(twitterData);
    }).then(() => {
        twitterData.forEach((response) => {
            response.engagement_score = (response.likes_count + response.retweet_count)/response.followers_count;
        })
        return P.resolve(twitterData);
    }).then(()=>{
        res.setHeader("Cache-Control", "max-age = 30");
        const fields = ['rank' , 'engagement_score'];
        const json2csvParser = new Json2csvParser({ fields });
        const csv = json2csvParser.parse(twitterData);
        console.log(csv);
        res.status(200).json(twitterData);
    }).catch((err) => {
        console.log(err);
        res.status(400).json(err);
    })
});

app.get('/popularTweets', (req,res) =>{
    let popularTweets =[{
        "user_id": 1469101279,
        "twitter_handle": "aantonop",
        "user_name": "Andreas M. Antonopoulos",
        "tweet_id": 1005553927822172200,
        "popular_tweet_content": "Many people will be lured into this space through cliches like \"blockchain not Bitcoin.\" Others will be drawn by the price. But this radical experiment will be sustained by those who stayed for the principles. https://t.co/tTMnbXYAwm",
        "followers_count": 431456,
        "retweet_count": 309,
        "likes_count": 1005
    },{
        "user_id": 1333467482,
        "twitter_handle": "coindesk",
        "user_name": "CoinDesk",
        "tweet_id": 1005037839330037800,
        "popular_tweet_content": "Which Way? Bitcoin's Low Volatility May Force Big Move https://t.co/EmxLMZaAJa https://t.co/dS5loG2QiR",
        "followers_count": 732251,
        "retweet_count": 50,
        "likes_count": 99
    },{
        "user_id": 2347049341,
        "twitter_handle": "voxdotcom",
        "user_name": "Vox",
        "tweet_id": 1005506067168743400,
        "popular_tweet_content": "Bitcoin mining now uses more energy than entire countries: https://t.co/2TaWKjVC5V\n\nIt’s a sign of just how big bitcoin has become, but what does the future hold? Watch the newest episode of Explained for more: https://t.co/XMktthK7Sl https://t.co/wjqs1AALjc",
        "followers_count": 725458,
        "retweet_count": 19,
        "likes_count": 40
    }
    ]
    res.status(200).json(popularTweets);
});

app.get('/price', (req,res) =>{
    let options= {
        uri: 'http://192.168.43.86:8001/getPrice/',
    }

    rp(options).then((result) => {
        res.status(200).json(result);
    });
})

app.get('/topTweets', (req,res) =>{
    let options= {
        uri: 'http://192.168.43.86:8001/popularTweets/',
    }

    rp(options).then((result) => {
        res.status(200).json(result);
    });
})

app.get('/popularInfluencers', (req,res) =>{
    let options= {
        uri: 'http://192.168.43.86:8001/popularInfluencers/',
    }

    rp(options).then((result) => {
        res.status(200).json(result);
    });
})



function getTweets(data){
    return client.get('statuses/user_timeline', {
        user_id : data.user_id,
        count: 20,
        tweet_mode: 'extended',
        include_rts: false,
        exclude_replies: true
    }).then((result) => {
        data.user_tweets = [];
        result.forEach(response => {
            data.user_tweets.push({
                tweet_content: response.full_text,
                tweet_date : response.created_at 
            })
        });
        return P.resolve(data);
    }).then(()=> {
        let options= {
            uri: 'http://api.twittercounter.com/',
            qs : {
            apikey: '4a1185a5bbc61fe63a23e333b056b256',
            twitter_id: data.user_id
            }
        }

        return rp(options).then((result) => {
            result = JSON.parse(result);
            data.rank = result.rank;
            return P.resolve(data);
        });
    })
}

app.listen(3000, () => console.log('Example app listening on port 3000!'))