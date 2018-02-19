const expect = require("chai").expect
const Player = require("./gameInterface.js").Player
//const test = require("./rpc_server.js").test

describe("",()=>{
    it("", ()=>{
        console.log("player %s", Player)
        p = new Player(()=>2, "test")
        expect(p.queueName).to.equal("test")

    })

})
