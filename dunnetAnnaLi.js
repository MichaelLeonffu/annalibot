//Main Spooky Anna Li

const discord 	= require("discord.js") 
const client 	= new discord.Client()

client.on('ready', () => {
	console.log(`
		Dunnet`
	)
	console.log(`Logged in as ${client.user.tag}!`)
})

var channelAttach

var gameEnable = false
var toggleCommand = false

client.on('message', message => {

	//configure command toggleing
	if(message.content == "toggle command"){
		toggleCommand = !toggleCommand
		return;
	}

	//if message starts with ; in normal operations skip it
	if(!toggleCommand){
		//normal, then ;TEXT is a comment
		if(message.content[0] == ';'){
			return;
		}
	}else{
		//not normal, then ;TEXT is a command
		if(message.content[0] != ';'){
			return;
		}

		//remoev the first ;
		message.content = message.content.substring(1);
	}

	if(message.content.includes("game pause")){
		gameEnable = false
		message.react('⏸️')
	}

	if(gameEnable && channelAttach != undefined && !message.author.bot && message.channel == channelAttach){
		//once we have locked on to a channel
		//then forward the contetns of its message out
		console.log(message.content)
	}

	if(message.content.includes("game startu")){
		gameEnable = true
		message.react('⏯')
	}

	if(message.content.includes("lock on this channel") ){
		// console.log("channel attached to")
		channelAttach = message.channel
		message.reply("🔒 channel has been locked on to 🔒")
	}


})

client.login(require('./config').apiKey.discord)

//LOGIC FOR SENDING MESSAGES

// Get process.stdin as the standard input object.
var standard_input = process.stdin;

// Set input character encoding.
standard_input.setEncoding('utf-8');

// Prompt user to input data in console.
console.log("Please input text in command line.");

// When user input data and click enter key.
standard_input.on('data', function (data) {

    // User input exit.
    if(data === 'exit\n'){
        // Program exit.
        console.log("User input complete, program exit.");
        process.exit();
    }else
    {
    	if(channelAttach != undefined)
        // Print user input in console.
        // console.log('User Input Data : ' + data);
       		channelAttach.send(data)
    }
});