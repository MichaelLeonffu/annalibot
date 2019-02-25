//Main Spooky Anna Li

const discord 	= require("discord.js") 
const client 	= new discord.Client()

client.on('ready', () => {
	console.log(`
		Turning off inhibitors...
		Enabling spooky...
		Designing spooky content...
		Implementing the element of surprise...
		Creating spooky failsafe...
		Finalizing spooky algorithm...
		Spooky on standby 👻`
	)
	console.log(`Logged in as ${client.user.tag}!`)
})

client.on('message', message => {
	//get ready for spooky!

	console.log("SPOOKED!!!! 👻")

	if(Math.random() < Math.random())
		if(message.guild.emojis.get('318986211379118081') != undefined)
			message.react(message.guild.emojis.get('318986211379118081'))
		else
			message.react('👻')
	else if(Math.random() > Math.random())
		message.react('👻')
	else
		message.react('🎃')
})

client.login(require('./config/apiKey').apiKey)