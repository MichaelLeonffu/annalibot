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

	if(Math.random() < 0.5){
		console.log("SPOOKED!!!! 👻")
		message.react('👻')
	}else
		console.log("Failed! to spooked!!!! 👻")
})

client.login(require('./config').apiKey.discord)
