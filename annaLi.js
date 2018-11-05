//Main Anna Li

const config		= require('./config')

const Discord 		= require("discord.js")
const client 		= new Discord.Client()

const MongoClient 	= require('mongodb').MongoClient
const assert 		= require('assert')

const math 			= require('mathjs')
const axios			= require('axios')

//Any things that need to be passed into all the rest of the code as sync should be placd here:
function initialize(callback){
	MongoClient.connect(config.mongodb.uri, function(err, client) {
		assert.equal(null, err)
		let db = client.db(config.mongodb.db)
		callback(db)
	})
}

//initialize everything
initialize((db) =>{

client.on('ready', () => {
	console.log(`Logged in as ${client.user.tag}!`)
})

client.on('message', 		data =>{genericEventHandle('message', 	'message', 			data)})
client.on('messageDelete', 	data =>{genericEventHandle('message', 	'messageDelete', 	data)})

client.on('guildCreate', 	data =>{genericEventHandle('guild', 	'guildCreate', 		data)})

client.login(config.apiKey.discord)

})

//allows new events to be easily be added
function genericEventHandle(type, subType, event){
	//code which does stuff to all events
	switch(type){
		case 'message':
			genericMessageHandle(subType, event)
			break
		case 'guild':
			genericGuildHandle(subType, event)
			break
		default:
			console.log('fail generic EventHandel thingy' + type)
	}
}

function genericGuildHandle(type, guild){
	//code which does stuff to this particular event
	switch(type){
		case 'guildCreate':
			guildCreateHandle(guild)
			break
		default:
			console.log('fail' + type)
	}
}

function guildCreateHandle(guild){
	console.log(guild)
}

function genericMessageHandle(type, message){
	//code which does stuff to this particular event
	switch(type){
		case 'message':
			messageHandle(message)
			break
		case 'messageDelete':
			messageDeleteHandle(message)
			break
		default:
			console.log('fail' + type)
	}
}

function messageHandle(message){
	console.log(message.content)
}

function messageDeleteHandle(message){
	console.log(message.content + " LOL")
}





