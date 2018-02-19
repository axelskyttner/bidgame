
const express = require('express')
var bodyParser = require('body-parser')
const app = express()
app.use(bodyParser.json())

app.get('/newGame', function(req, res){

  try {
    var playerStruct = JSON.parse(req.query.players)

    var extraPlayers = Math.max(0, 2 - playerStruct.players.length)

    var players = playerStruct.players
    for (var i=0;i<extraPlayers;i++){
      players.push(generateDummyPlayer(i+1))
    }

    var result = newGame(playerStruct.players)

    res.json(result)
  } catch (err) {
    res.status(500).send('Something broke! ' + err.message)
  }
})

// Example call
//http://localhost/newGame?players={%22players%22:[{%22id%22:%22olle%22,%22code%22:%22var%20myFunction%20=%20function%20(players,%20color,%20transaction_list)%20{%20return%2010%20}%22}]}

app.listen(80, () => console.log('Example app listening on port 80!'))




function newGame(players) {

  var result
  var history = []
  for (var i=0;i<100;i++){
    result = runBidGameRound(players, history, i)
    if (result.endOfGame) {
      break
    }
    history = result.history
  }


  var winnings = {}
  history.forEach(function (item) {
    if (item.winnings !== 'NONE') {
      var playerScore = winnings[item.playerId] || {}
      playerScore[item.winnings] = playerScore[item.winnings] === undefined ? 1 : playerScore[item.winnings] + 1
      winnings[item.playerId] = playerScore
    }
  })

  return {
    winnings: winnings,
    history: result.history
  }
}



function generateDummyPlayer (i) {
  return {id: "Nisse " + i, code: "var myFunction = function (players, color, transaction_list) { return 5 }"}
}




function runBidGameRound(players, history_, roundId){   //ToDO: Create Player struct
  var history = history_.slice()

  var colorList = ["RED", "BLUE", "GREEN"]

  var gameRoundColor = colorList[randomIntFromInterval(0, colorList.length-1)]
  var playerList = JSON.stringify(players.map(player=>player.id))


  var bids = players.map(function (player,index) {
    var historyList = JSON.stringify(history)
    var code = "(function(){" + player.code + "\n" + "return myFunction("+playerList+",'"+gameRoundColor+"',"+historyList+") })()"     //TODO: Add jslint
    var result = eval(code)
    return {bid: result, player: player}
  })

  var highscore = -1
  var bestPlayer = ""
  bids.forEach(function (result) {
    if (result.bid > highscore && playerCanAffordBid(result.player.id, history) ) {
      bestPlayer = result.player.id
      highscore = result.bid
    }
  })

  bids.forEach(function (result) {
    if (result.player.id === bestPlayer) {
      history.push({playerId: result.player.id, bid: result.bid, winnings: gameRoundColor, round: roundId})   //ToDO Create HistoryStruct
    } else {
      history.push({playerId: result.player.id, bid: result.bid, winnings: 'NONE', round: roundId})
    }
  })


  var endOfGame = endConditionCheck(history)

  return {
    history: history,
    endOfGame: endOfGame
  }

  function playerCanAffordBid (playerId, history) {
    var bids = history.filter(function (item) {
      return item.playerId === playerId
    })

    var sum = 0
    bids.forEach(function (item) {sum += item.bid})

    return sum <= 100
  }

  function endConditionCheck(history) {
    var winnings = {}
    history.forEach(function (item) {
      if (item.winnings !== 'NONE') {
        winnings[item.winnings] = winnings[item.winnings] === undefined ? 1 : winnings[item.winnings] + 1
      }
    })

    var keys = Object.keys(winnings)
    var fiveEqual = false
    keys.forEach(function(key) {
      if (winnings[key] >= 5) {
        fiveEqual = true
      }
    })

    return fiveEqual
  }
}


function randomIntFromInterval(min,max)
{
    return Math.floor(Math.random()*(max-min+1)+min);
}
