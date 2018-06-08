//Main Anna Li

// const express 		= require('express')
// const app			= express()
// const path 			= require('path')
// const port 			= process.env.PORT || 3000
// const morgan 		= require('morgan')
// const bodyParser 	= require('body-parser')

const Discord 		= require("discord.js")
const client 		= new Discord.Client()

const MongoClient 	= require('mongodb').MongoClient
const assert 		= require('assert')
const url 			= 'mongodb://localhost:27017'

const math 			= require('mathjs')

// app.use(morgan('dev')) // log every request to the console
// app.use(bodyParser.json())
// app.use(bodyParser.urlencoded({
// 	extended: true
// }))

// app.use(cookieParser())

// app.listen(port)
// console.log('Server started on port ' + port)

//Importing libarays

//const messages 		= require('./messages')

let pickRandomMessage = function(arrayOfRandomMessages){
	console.log('Using pickRandomMessage')
	return arrayOfRandomMessages[math.round(math.random()*(arrayOfRandomMessages.length-1))]
}

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
	if(message.author.username == 'Toon'){
		console.log('Ignored:', message.author.username)
		return
	}

	if(false && messageContent.includes('anna') && messageContent.includes('li') && message.author.bot === false){
		MongoClient.connect(url, function(err,client){
			var db = client.db('AnnaLi')
			console.log('Connected to the AnnaLi database')
			//var randomType = pickRandomMessage(['res_prefix','res_reaction','res_continue','res_end'])
			//console.log('randomType',randomType)
			db.collection('conversations').aggregate([
				// {$match:{$expr:{
				// 	$eq:['$type',randomType]
				// }}},
				{$match:{$expr:{$or:[
					{$eq:['$type','res_prefix']},
					{$eq:['$type','res_reaction']},
					{$eq:['$type','res_continue']},
					{$eq:['$type','res_end']}
				]}}},
				{$project:{
					_id:0
				}}
				],cursorHandle
			)

			function cursorHandle(err, cursor){
				if(err){
					console.log(err)
					return
				}else{
					cursor.toArray(messageFound)
				}
			}

			function messageFound(err, messagesResponses){
				if(err){
					console.log(err)
					client.close()
					return
				}
				//console.log(messagesResponses)
				var completeMessages = []
				for (var i = 0; i < messagesResponses.length; i++) {
					//messagesResponses[i]
					for (var j = 0; j < messagesResponses[i].count; j++) {
						completeMessages.push(messagesResponses[i].message)
					}
				}
				//console.log('messagesResponses',completeMessages)

				message.channel.send(pickRandomMessage(completeMessages))

				client.close()
			}
		})
	}

	//If username is toon then reply baka
	// if(message.author.username == 'Toon' && message.author.bot === false){
	// 	console.log('user:',message.author.username,'replying with: baka')
	// 	message.reply('BAKA!')
	// 	return
	// }

	//If you ask anna a question
	// if(messageContent.includes('?') && messageContent.includes('anna') && message.author.bot === false){

	// 	const responses = ['Yeah', 'Spooky', 'No.', 'baka', 'lol', 'k', 'nande?', 'NANI?', '¯\\_(ツ)_/¯', 'S a d...']

	// 	message.channel.send(pickRandomMessage(responses))
	// }

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

	if(messageContent.includes('join') && message.author.bot === false){
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

	//LACKS PERMISSIONS
	if(messageContent.includes('pink') && message.author.bot === false){
		console.log('pink command detected')

		// Set the color of a role of R:255, G:209, B:220
		role.setColor([255,209,220]).then(r =>{
			console.log(`Set color of role ${r}`)
		}).catch(err =>{
			console.log(err)
		})

		message.reply('pink? :3c')
	}

	if(messageContent.includes('flip') && message.author.bot === false){
		console.log('flip command detected')

		let coinFlip = math.random()

		if(coinFlip < 0.49){
			//tails
			message.reply(pickRandomMessage(['tails','tails!','wow tails']))
		}else if(coinFlip > 0.51){
			//heads
			message.reply(pickRandomMessage(['heads','heads!','wow heads']))
		}else{
			console.log('coin flip landed on side!')
			message.reply(pickRandomMessage(['IT LANDED ON ITS SIDE', 'Omg... it\'s on its side!']))
		}
	}

	if(messageContent.includes('scan') && message.author.bot === false){
		console.log('scan command detected')

		console.log('SCAN-----------------------------------------\n',message.guild.roles.get('407709451534204928'))


		message.reply('Scanning... 😀')
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