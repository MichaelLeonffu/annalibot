const Discord 		= require("discord.js")
const client 		= new Discord.Client()

const MongoClient 	= require('mongodb').MongoClient
const assert 		= require('assert')
const url 			= 'mongodb://localhost:27017'

const math 			= require('mathjs')

//Importing libarays

//const messages 		= require('./messages')

client.on('ready', () => {
	console.log(`Logged in as ${client.user.tag}!`)
})

client.on('message', message => {
try{

	let messageContent = message.content.toLowerCase()

	//Dont set messages in mainchat or weeb-meme-land
	if(message.channel.name === 'mainchat' || message.channel.name === 'weeb-meme-land'){
		console.log('Ignored:', message.channel.name)
		return
	}

	//ignore thses users
	if(message.author.username == 'aFrenchToastMan'){
		console.log('Ignored:', message.author.username)
		return
	}

	//If username is toon then reply baka
	if(message.author.username == 'Toon' && message.author.bot === false){
		console.log('user:',message.author.username,'replying with: baka')
		message.reply('BAKA!')
		return
	}

	//If you ask anna a question
	if(messageContent.includes('?') && messageContent.includes('anna') && message.author.bot === false){

		const responses = ['Yeah', 'Spooky', 'No.', 'baka', 'lol', 'k', 'nande?', 'NANI?', '¯\\_(ツ)_/¯', 'S a d...']

		message.reply(responses[math.round(math.random()*(responses.length-1))])
	}

	//Anna Li can find your pic for you
	if(messageContent.includes('mypic') && message.author.bot === false){
		 message.reply(message.author.avatarURL)
	}

	//You spooked an Anna Li! She boops you!
	if (messageContent.includes('spooky') && message.author.bot === false){
		console.log(message.author.username,'spookyed Anna Li!')
		message.reply('boop!!!!')
	}

	//If Anna Li is in a call, she'll leave and be sad
	if (messageContent.includes('leave') && message.author.bot === false){

		const channel = message.member.voiceChannel
		channel.leave()
		message.reply('QQ...')
	}

	if (messageContent.includes('test') && message.author.bot === false){

		// console.log('CONSOLELOG----------------------------\n', client.emojis.get('318986211379118081'))
		// console.log('NUMBER2----------------------------\n', client.emojis.find('name','spooky'))

		//const spooky = client.emojis.find('name','spooky')
		//const spooky = client.emojis.get('407735054425653248')


		message.reply('🙃')

		const channel = message.member.voiceChannel

		channel.join().then(connection =>{
			console.log(connection)
			const dispatcher = connection.playFile('./nya.mp3')
			console.log('dispatcher', dispatcher.volumeLogarithmic)
			dispatcher.setVolumeLogarithmic(0.10)
			console.log('SETVOLUME', dispatcher.volumeLogarithmic)

		}).catch(err =>{
			console.log(err)
		})

		// Play a broadcast
		// const broadcast = client
		// 	.createVoiceBroadcast()
		// 	.playFile('./test.mp3');
		// const dispatcher = voiceConnection.playBroadcast(broadcast);
		message.reply('I Test! :3c ')
	}

	if (messageContent.includes('join') && message.author.bot === false){
		console.log('join command detected')

		const channel = message.member.voiceChannel	//Need to check if in voice channel

		channel.join().then(connection =>{
			//console.log(connection)
			console.log('Message detected in:', message.channel.name)
			message.reply('I joined ;) ')
		}).catch(err =>{
			console.log(err)
		})

	}

	//mongodb init
	// MongoClient.connect(url, function(err, db) {
	// 	assert.equal(null, err);
	// 	var collection = db.collection('todo')

	// 	switch (msg.content.toLowerCase()) {
	// 		case 'l!todo':
	// 		collection.aggregate([
	// 			{$sort:{name:1}}
	// 		],
	// 			function(err, docs){
	// 			assert.equal(null, err);
	// 				console.log('AGGERGATION',docs)
	// 				for (var i = 0; i < docs.length; i++) {
	// 					msg.reply(docs[i].todo)
	// 				}
	// 			}
	// 		)

	// 		break;
	// 		default:
	// 		console.log('did not detect message')
	// 		break;
	// 	}
	// 	if (msg.content.toLowerCase() === 'ping') {
	// 		console.log('detected ping yay')
	// 		msg.reply('Pong!')
	// 		msg.delete(5000)
	// 		console.log('detleted pong')
	// 	}

	// 	if (msg.content.toLowerCase().includes('Pong!')) {
	// 		console.log('DETECTED PONG',msg.content.toLowerCase())
	// 		msg.delete(1000)
	// 	}

	// 	// console.log('msg', msg)
	// 	// var toLog = msg.constructor
	// 	// console.log('msgpart', toLog)
	// 	// console.log('typeof', typeof toLog)

	// 	// db.collection('msg').insertOne({'message':msg},
	// 	//  function(err, result){ 
	// 	//    assert.equal(err, null)
	// 	//    console.log("Inserting doc")
	// 	//  }
	// 	// )

	// 	var message = msg.content.toLowerCase()
	// 	console.log(message)
	// 	if(message.includes('l!addtodo ')){
	// 		message = message.replace('l!addtodo ','')
	// 		console.log(message)
	// 		msg.reply(message)

	// 		var docToInsert = {
	// 			todo: message
	// 		}
	// 		collection.insertOne(docToInsert,
	// 			function(err, result){ 
	// 				assert.equal(err, null)
	// 				console.log("Inserting doc", docToInsert)
	// 			}
	// 		)
	// 	}

	// 	//ends mongodb connection
	// 	db.close()
	// });
}
catch(err){
	console.log(err)
	message.reply('That didn\'t make sense 😵')
}
})

const apiKey = require('./config/apiKey').apiKey

client.login(apiKey)