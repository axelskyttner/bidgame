var Player = require("./gameInterface.js").Player

function callback( currentColor, previousBid, transactionList){
    console.log("color: %s", currentColor)
    console.log("previousBid: %d", previousBid)
    console.log("transactionList: ", transactionList)

    return 2

}
var p1 = new Player(callback, "player-2-queue");

p1.start()
