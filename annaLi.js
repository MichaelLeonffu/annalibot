//AnnaLi by Michael Leonffu

const config		= require('./config')

const Discord 		= require("discord.js")
const client 		= new Discord.Client()

const MongoClient 	= require('mongodb').MongoClient
const assert 		= require('assert')

const math 			= require('mathjs')
const axios			= require('axios')

const requests 		= require('./requests/requests')

//Any things that need to be passed into all the rest of the code as sync should be placd here:
function initialize(next){
	MongoClient.connect(config.mongodb.uri, function(err, client) {
		assert.equal(null, err)
		//TODO: add logic to attempt to reconnect until connection works, at every config X intervals
		let db = client.db(config.mongodb.db)
		next(db)
	})
}

//initialize everything
initialize((db) =>{

	//change to genertic event handle
	client.on('ready', 			() =>	{console.log(`Logged in as ${client.user.tag}!`)})

	client.on('message', 		event =>{genericEvent(db, 'message', 	'message', 			event)})
	client.on('messageDelete', 	event =>{genericEvent(db, 'message', 	'messageDelete', 	event)})
	client.on('guildCreate', 	event =>{genericEvent(db, 'guild', 		'guildCreate', 		event)})

	client.login(config.apiKey.discord)

})

//allows new events to be easily be added
function genericEvent(db, type, subType, event){
	//code which does stuff to all events

	db.collection('logs').insertOne(	//TODO finsih adding log to all the methods....
		{
			data: 'test',
			time: new Date()
		}, (err, result) =>{
			if(err); //do something
			console.time(result.insertedId) //start timer
			let log = {logsId: result.insertedId}
			switch(type){
				case 'message': 	genericMessageHandle 	(db, subType, event, log);	break
				case 'guild': 		genericGuildHandle		(db, subType, event, log);	break
				default: 			console.log('fail generic EventHandel thingy' + type)
			}
		}
	)
}

function genericGuildHandle(db, type, guild, log){
	//code which does stuff to this particular event
	switch(type){
		case 'guildCreate': 	guildCreateHandle(db, guild); 	break
		default: 				console.log('fail' + type)
	}
}

function guildCreateHandle(db, guild){
	console.log(guild)
}

function genericMessageHandle(db, type, message, log){

	//messages are always from channels, but sometimes from guilds.
		//gather config information for this partucular event, this can be more generic latter.
		//perhapse all events have users as such etc.
	//meta information gatherers can be made as well such that certain databse calls shouldnt be needed

	//TODO: add a timer, search by time then have a promise to get more data. this is quicker than complsing lots of data per message
	//TODL: add a thing that deltays the resoionces which then it cna read new inputs and changethe reponses

	// message.guild != null is false when guild is not present
	// message.channel.id != null is false when TextChannel is returned. DMChannel and GroupDMChannel have ids
	db.collection('guilds').findOne(	//EACH OF THESE SHOULD BE SEPERATE SUCH THAT OTHER "generric______" CAN REUSE THEM!
		{
			_id: message.guild != null ? message.guild.id : 'null' //techically should skip this aggregate.
		}, (err, guild) =>{ //gathers guild information
			if(err);	//add logger here
			if(config.verbose.mongodb.results) console.info('\x1b[36m%s\x1b[0m', '[genericMessageHandle-guild]: ', guild)
			db.collection('channels').findOne(
				{
					_id: message.channel.id != null ? message.channel.id : message.channel.parentID //has parentID for "TextChannel" part of guild
				}, (err, channel) =>{
					if(err); //add logger here too
					if(config.verbose.mongodb.results) console.info('\x1b[36m%s\x1b[0m', '[genericMessageHandle-channel]: ', channel)
					db.collection('users').findOne(
						{
							_id: message.author.id
						}, (err, user) =>{
							if(err); //""
							if(config.verbose.mongodb.results) console.info('\x1b[36m%s\x1b[0m', '[genericMessageHandle-users]: ', user)
							
							//code which does stuff to this particular event

							let configs = {
								guild: guild,
								channel: channel,
								user: user
							}

							pipelineGenerator(db, configs, log, 
								(err, pipeline) =>{
									// switch(type){
									// 	case 'message': 		messageHandle(db, configs, pipeline, message, log); 		break
									// 	case 'messageDelete': 	messageDeleteHandle(db, configs, pipeline, message);	break
									// 	default: 				console.log('fail' + type)
									// }

									//use case of message and deleted message handle is to have any methods that work for either or all
									//messagse of that type are handled. althoguh a pipe can be used, this will force it.
									//i.e recording messages, if all messages should be recorded then it can go though the handle.

									if(err); //""
									pipelineEngine(db, pipeline, {message: message, action: genericAction}, log)
								}
							)
						}
					)
				}
			)
		}
	)
}

//generates the pipeline for the methods to use; doesn't need data to generate pipeline (I think!), CHECK LATTER TODO!
function pipelineGenerator(db, configs, log, next){
	//configs are given in varible amount? array, can have configs for server, guild, user, etc
	//configs contains information on which piplines to use if any custom pipelines are made

	//finds all the requiered requests which are mandatory by config file.
	db.collection('requests').find(
		{
			$or:[{_id: 'hi'}]	//gathering the pipeline data using the configs
		},(err, requestsData) =>{
			if(err) return console.error('\x1b[31m%s\x1b[0m', '[pipelineGenerator-err]: ', err) //replace with ending sequence! using "log"

			requestsData.toArray((err, requests) =>{
				if(err);

				let pipeline = [requests]

				pipeline = ['DNEPipe', 'nullPipe', 'noBotReplyPipe', 'repeatAction']

				console.log('\x1b[36m%s\x1b[0m', '[pipelineGenerator-pipline]: ', pipeline)

				err = null //change this to which ever errors if err

				next(err, pipeline)
			})
		}
	)
}

//recursively
function pipelineEngine(db, pipeline, data, log){
	//runs the pipelines.... boop beep

	//base case
	if(pipeline.length <= 0)
		// return data.action(db, 'sendMessage', data, log) //should be error
		return console.error('ERROROROROORROOR')

	//action case (good base case)
	if(pipeline.length == 1)
		return genericAction(db, pipeline.shift(), data, log)

	pipelineManager(pipeline.shift())(db, data, log, (options) =>{
		if(options.escape == true) //escape somehow!
			return genericAction(db, 'escape!', 'data', log)
		if(options.data != null)
			data = options.data //this is how pipelines talk

		pipelineEngine(db, pipeline, data, log)
	})
}

function pipelineManager(pipeline){
	//add logic

	switch(pipeline){
		case 'noBotReplyPipe': 	return noBotReplyPipe; 	break
		default: 				return nullPipe;		break
		// default: return console.error('Q W Q'); 		break
	}
}

//the default empty could not find pipe option
function nullPipe(db, data, log, next){
	next({})
}

function noBotReplyPipe(db, data, log, next){
	if(data.message.author.bot) 	return next({escape: true})
	next({})
}

//this is how all things should end, with an action.
function genericAction(db, type, data, log){
	switch(type){
		case 'repeatAction': data.message.channel.send(data.message.content); 	break
		// case 'repeatAction': console.info(data.message.content); 	break
		default: 	console.error('LOL FIX THIS' + type); break
	}
}

function sendMessage(db, data){

}

function messageHandle(db, config, pipeline, message, log){
	// console.log(message.content != null)
	// console.warn(message.guild != null)
	// console.error(message.channel != null)

	pipelineEngine(db, pipeline, {message: message, action: genericAction}, log)

	// genericAction(db, 'sendMessage', {message: message})

	return
	console.log('log')
	console.info('info')
	console.warn('warn')
	console.error('error')
	// console.clear()
	// console.table([[1,2,3,4],[1,2,3,3,1,1],[1,2,3,1,1,2,3]])
	console.group('somegroup')
	console.time('timer1')
	console.timeLog('timer1', '')
	console.timeEnd('timer1')
	console.timeLog('timer1')
	console.timeEnd('timer1')
	console.assert(false, 'PIGS FLY')
	console.assert(true)
	console.groupEnd('somegroup')
}

function messageDeleteHandle(db, config, pipeline, message){
	console.log(message.content + " Deleted!")
}



