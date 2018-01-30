const Discord = require("discord.js")
const client = new Discord.Client()

var MongoClient = require('mongodb').MongoClient
var assert = require('assert')
var url = 'mongodb://localhost:27017'

client.on('ready', () => {
	console.log(`Logged in as ${client.user.tag}!`)
})

client.on('message', msg => {

	//mongodb init
	MongoClient.connect(url, function(err, db) {
		assert.equal(null, err);
		var collection = db.collection('todo')

		switch (msg.content.toLowerCase()) {
			case 'l!todo':
			collection.aggregate([
				{$sort:{name:1}}
			],
				function(err, docs){
				assert.equal(null, err);
					console.log('AGGERGATION',docs)
					for (var i = 0; i < docs.length; i++) {
						msg.reply(docs[i].todo)
					}
				}
			)

			break;
			default:
			console.log('did not detect message')
			break;
		}
		if (msg.content.toLowerCase() === 'ping') {
			console.log('detected ping yay')
			msg.reply('Pong!')
			msg.delete(5000)
			console.log('detleted pong')
		}

		if (msg.content.toLowerCase().includes('Pong!')) {
			console.log('DETECTED PONG',msg.content.toLowerCase())
			msg.delete(1000)
		}

		// console.log('msg', msg)
		// var toLog = msg.constructor
		// console.log('msgpart', toLog)
		// console.log('typeof', typeof toLog)

		// db.collection('msg').insertOne({'message':msg},
		//  function(err, result){ 
		//    assert.equal(err, null)
		//    console.log("Inserting doc")
		//  }
		// )

		var message = msg.content.toLowerCase()
		console.log(message)
		if(message.includes('l!addtodo ')){
			message = message.replace('l!addtodo ','')
			console.log(message)
			msg.reply(message)

			var docToInsert = {
				todo: message
			}
			collection.insertOne(docToInsert,
				function(err, result){ 
					assert.equal(err, null)
					console.log("Inserting doc", docToInsert)
				}
			)
		}

		//ends mongodb connection
		db.close()
	});
})

const apiKey = require('./config/apiKey').apiKey

client.login(apiKey)