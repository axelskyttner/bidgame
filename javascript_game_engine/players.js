const axios = require('axios')

const players = JSON.stringify({"players":[
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
console.log('players', players)
axios.get('http://localhost:5000/newGame?players=' + players).then(res => {

  console.log('res', res.data)
})

