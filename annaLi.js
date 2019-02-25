//AnnaLi by Michael Leonffu

const config		= require('./config')

const Discord 		= require("discord.js")
const client 		= new Discord.Client()

const MongoClient 	= require('mongodb').MongoClient
const assert 		= require('assert')

const math 			= require('mathjs')
const axios			= require('axios')

const pipeData 		= require('./pipes/pipes')

//pipeline loader should exist: console logs as the pipes are being imported
//creates a map of pipe ids to the pipe methods. by loading though each pipe

const pipes = {}		///this is the final map

function pipeLoader(){

}

//recusively finds all pipes from pipeData and adds it to the pipes 
function pipeLoaderEngine(pipes, pipeData){

	let keys = Object.keys(pipeData)							//gets all the keys of this object

	for(let i = 0; i < keys.length; i++){						//for each key in the pipeData
		if(typeof pipeData[keys[i]] == 'object')				//checks if it's an object
			if(pipeData[keys[i]].run == undefined)				//checks if exsists
				pipeLoaderEngine(pipes, pipeData[keys[i]])		//recusrively add more if incomplete
			else if(typeof pipeData[keys[i]].run == 'function')	//checks if its a pipe
				pipes[keys[i]] = pipeData[keys[i]]				//add the pipe
			else;												//not a pipe! not an object!
				//log it //TODO!
	}
}

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

	if(message.guild.id != config.dev.server)
		return console.log('SAVED THE DAY!')

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
							if(config.verbose.mongodb.results) console.info('\x1b[36m%s\x1b[0m', '[genericMessageHandle-user]: ', user)
							db.collection('configurations').findOne(
								{
									_id: 'config.configurations.masterConfigID' //create
								}, (err, configuration) =>{
									if(err); //""
									if(config.verbose.mongodb.results) console.info('\x1b[36m%s\x1b[0m', '[genericMessageHandle-configuration]: ', configuration)

									//code which does stuff to this particular event

									//example one for now
									let exampleConfiguration = {
										requests:[
											//object ids?
											'todo'
										]
										// requests:[
										// 	//overriding logic
										// 	//maybe can be an object rather than an array?
										// 	{
										// 		name: 'addTodo',
										// 		pipeline:[ //maybe can be an object rather than an array?

										// 		]
										// 	},
										// 	{
										// 		name: 'readTodo',
										// 		pipeline:[ //maybe can be an object rather than an array?

										// 		]
										// 	}
										// ]
									}

									configuration = exampleConfiguration

									let configs = {
										guild: guild,
										channel: channel,
										user: user,
										masterConfig: configuration, //replace latter 
										//REMOVE THIS LATTER
									}

									//CONFIGUREATION LOGIC HERE! its configs and datas.

									let examplePipeline = [
										{
											'$messageInterpretToRequest':[
												'$addTodo',
												'$readTodo'
											]
										}
									]

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

				let addTodo = [
					{
						procedure: 'request',
						type: 'message',
						id: 'noBotReplyPipe',
						args: null
					},
					{
						procedure: 'request',
						type: 'message',
						id: 'addToTODO',
						args: null
					},
					{
						procedure: 'action',
						type: 'message',
						id: 'sendMessage',
						args: null
					}
				]

				let readTodo = [
					{
						procedure: 'request',
						type: 'message',
						id: 'noBotReplyPipe',
						args: null
					},
					{
						procedure: 'request',
						type: 'message',
						id: 'readFromTodo',
						args: null
					},
					{
						procedure: 'action',
						type: 'message',
						id: 'sendMessage',
						args: null
					}
				]

				let finalPipe = [
					{
						procedure: 'request',
						type: 'message',
						id: 'noBotReplyPipe',
						args: null
					},
					{
						procedure: 'request',
						type: 'message',
						id: 'messageInterpretToRequest',
						args: [addTodo, readTodo]
					}
				]

				pipeline = finalPipe

				//this can reflect the config better and be more consisce

				loggerAid(config.verbose.pipeline, 'info', 'cyan', '[pipelineGenerator-pipline]', pipelineToString(pipeline))

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
		return loggerAid(config.verbose.pipeline, 'info', 'red', '[pipelineEngine-pipline]', pipeline)
		// return data.action(db, 'sendMessage', data, log) //should be error
		// return console.error('Pipe end! pipe should always escape before ending this way.')

	let pipe = pipeline.shift()

	//pipe.args may be null!

	pipelineManager(pipe)(db, data, log, pipe.args, (options) =>{ //pipes should throw "(err, data)" where in err can have warnings or escape etc
		if(options.escape == true) //escape somehow!
			return genericAction(db, 'escape!', 'data', log)
		if(options.pipeline != null && options.pipeline.length > 0){ //returns a pipeline; escape can escape if wanted
			loggerAid(config.verbose.pipeline, 'info', 'cyan', '[pipelineEngine-pipeline][options-pipline-tiggered]', options.pipeline)
			return pipelineEngine(db, options.pipeline, data, log) //REMOVE RETURN
		}

		loggerAid(config.verbose.pipeline, 'info', 'green', '[pipelineEngine-pipeline][continue]', pipelineToString(pipeline))

		//NOTICE, the pipeline CAN be split into many: one evalutes the pipline above, the other
			//finishes the main pipeline
		pipelineEngine(db, pipeline, data, log) //this pipeline engine should end
	})
}

//finds and connects the pielines
function pipelineManager(pipe){
	//add logic

	//check pipeline quality TODO

	//temp
	if(pipes[pipe.type] == undefined || pipes[pipe.type][pipe.procedure] == undefined || pipes[pipe.type][pipe.procedure][pipe.id] == undefined){
		loggerAid(config.verbose.pipeline, 'warn', 'yellow', '[pipelineManager-pipe]', pipe)
		return nullPipe
	}

	loggerAid(config.verbose.pipeline, 'info', 'cyan', '[pipelineManager-pipe]', pipelineToString(pipe))
	return pipes[pipe.type][pipe.procedure][pipe.id].run //no need for switches

}

//the default empty could not find pipe option
function nullPipe(db, data, log, args, next){
	next({})
}

//this is how all things should end, with an action.
function genericAction(db, type, data, log){
	switch(type){
		case 'repeatAction': data.message.channel.send(data.message.content); 	break
		// case 'repeatAction': console.info(data.message.content); 	break
		default: 	loggerAid(config.verbose.pipeline, 'error', 'red', '[genericAction-type]', type); break
	}
}

function sendMessage(db, data){

}

//recusion
function pipelineToString(pipeline){
	//base
	if(pipeline.id != undefined) //or not an array
		if(pipeline.args != undefined && pipeline.args != null) //meaning it containds pipelines
			return '\x1b[35m' + pipeline.id + '\x1b[0m' + '(' + pipelineToString(pipeline.args) + ')]'
		else
			return '\x1b[35m' + pipeline.id + '\x1b[0m' + ']'
	finalString = ''
	for(let i = 0; i < pipeline.length; i++)
		finalString += '[' + pipelineToString(pipeline[i]) + ((i == pipeline.length-1)? '' : ', ')
	return finalString + ']'
}

//should log all into a logger file in portions... logger files should be named by instance? and running time.
//perhapse saving the logger file as data? tho all data shoulg be logged anways... :shrug:
//logger switcehs should be located here as well (from config)
//defaults should also be located here where default switches r chosen if no cohsen switcehs r found
//there is also ... 
function loggerAid(option, level, color, tag, data){
	if(option == false)
		return
	switch(color){
		case 'cyan': 	color = '\x1b[36m%s\x1b[0m'; break
		case 'red': 	color = '\x1b[31m%s\x1b[0m'; break
		case 'black': 	color = '\x1b[30m%s\x1b[0m'; break
		case 'green': 	color = '\x1b[32m%s\x1b[0m'; break
		case 'yellow': 	color = '\x1b[33m%s\x1b[0m'; break
		case 'blue': 	color = '\x1b[34m%s\x1b[0m'; break
		case 'magenta': color = '\x1b[35m%s\x1b[0m'; break
		case 'white': 	color = '\x1b[37m%s\x1b[0m'; break
		default: color = ''; break //bad color
	}
	switch(level){
		case 'error': 	console.error(color, tag, data); break
		case 'info': 	console.info(color, tag, data); break
		case 'warn': 	console.warn(color, tag, data); break
		default: 		console.log(color, tag, data); break
	}
}

function messageHandle(db, config, pipeline, message, log){
	// console.log(message.content != null)
	// console.warn(message.guild != null)
	// console.error(message.channel != null)

	// pipelineEngine(db, pipeline, {message: message, action: genericAction}, log)

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



