# bidgame
API for bidgame



# API for javascript game engine

cd javascript_game_engine
npm start

requiest url to localhost/newGame?players=...

Include a code block as a string that declares "var myBid = function () { .... return 0 }" 



Arguments include a player id list, the color of the current bid and a history with the following structure
```js
var history = [
    {playerId: "nisse", bid: 30, winnings: "BLUE", round: 0},
    {playerId: "olle", bid: 20, winnings: "NONE", round: 0},
    {playerId: "nisse", bid: 30, winnings: "BLUE", round: 1},
    {playerId: "olle", bid: 20, winnings: "NONE", round: 1}
  ]
```

Example code block
```js
var players = JSON.stringify({"players":[
  {
    id:"olle",
    code:"var myBid = function (players, color, history) { return Math.random() }"
  },
  {
    id:"nisse",
    code:"var myBid = function (players, color, history) { return 10 }"
  }
  ]
})

// To string example
function test () {
  //do some stuff
}

var code = "var myBid = " + test.toString()

```

Example call
http://localhost/newGame?players={%22players%22:[{%22id%22:%22olle%22,%22code%22:%22var%20myBid%20=%20function%20(players,%20color,%20transaction_list)%20{%20return%2010%20}%22}]}
