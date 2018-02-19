var amqp = require('amqplib/callback_api');


function Player(responseFunction, queueName){
    this.queueName = queueName
    this.responseFunction = responseFunction;

}


Player.prototype.start= function(){

    const callbackFunction = this.responseFunction;
    const queueName = this.queueName;

    amqp.connect('amqp://localhost', function(err, conn) {
            conn.createChannel(function(err, ch) {
                var q = queueName

                ch.assertQueue(q, {durable: false});
                ch.prefetch(1);
                console.log(' [x] Awaiting RPC requests');
                ch.consume(q, function reply(msg) {
                        console.log("msg.content.toString()", msg.content.toString())
                        inputString = JSON.parse(msg.content.toString())
                        console.log("inputString", inputString)
                        var color = inputString.color
                        var currentBid = inputString.bid
                        var transactionList = inputString["transaction-list"]

                        var response = callbackFunction( color,currentBid, transactionList)

                        ch.sendToQueue(msg.properties.replyTo,
                                new Buffer(response.toString()),
                                {correlationId: msg.properties.correlationId});

                        ch.ack(msg);
                        });
            });
});

}



module.exports = {

        Player:Player,
       test: 2

}
