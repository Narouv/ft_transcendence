import { GObjMngr } from "./GameObjectManager.js";
import { ReplicationManager } from "./ReplicationManager.js";
import InputManager from "./InputManager.js";

function sleep(ms)
{
	return new Promise((resolve, reject) => {
		setTimeout(() =>{resolve()}, ms)
	})
}

export class GameClient
{
	constructor(minFrameTime)
	{
		this.frameInfo = {
			
		}
		this.runGame = false;
		this.fps = 1;
		this.delta = 1;
		this.lastTickTime = 0;
		this.minFrameTime = minFrameTime;
		this.objMngr = new GObjMngr();
		this.settings = {
			keyBindings: [
				{ side: 'left', keyUp: 'KeyW', keyDown: 'KeyS' },
				{ side: 'right', keyUp: 'ArrowUp', keyDown: 'ArrowDown' }
			],
			
		}
		this.replication = new ReplicationManager(this);
	}

	calcFps()
	{
		if (this.delta)
			this.fps = (this.fps + (1 / this.delta)) / 2;
	}

	calcDelta()
	{
		this.delta = (Date.now() - this.lastTickTime) / 1000;
		this.lastTickTime = Date.now();
	}

	async gameLoop()
	{
		while (this.runGame)
		{
			this.calcDelta();
			this.calcFps();
		
			this.objMngr.runSimulation(this.delta);
			this.objMngr.syncDOM(this.delta);
			this.replication.updateServer()
	
			await sleep(this.minFrameTime);
		}
	}

	async startEngine()
	{
		target.innerHTML = this.htmlContent();
		this.objMngr.overlay.load()
		for (var binding of this.settings.keyBindings)
		{
			InputManager.preventAction[binding.keyDown] = true;
			InputManager.preventAction[binding.keyUp] = true;
		}
		if (this.runGame)
			return
		this.runGame = true;
		this.lastTickTime = Date.now();
		this.gameLoopPromise = this.gameLoop();
	}

	async stopEngine()
	{
		InputManager.preventAction = {}
		if (!this.runGame)
			return
		this.runGame = false;
		this.objMngr.overlay.unload()
		await this.gameLoopPromise
	}

	async endEngine()
	{
		await this.stopEngine()
		await this.disconnect()
	}

	async connect()
	{
		if (!await api.verifyAuthenticated())
		{
			ft_log("Not Authenticated - cant connect")	
			return;
		}
		return await this.replication.connect('/ws/tpong/')
	}

	initLobby(timeout)
	{
		return new Promise(async function(resolve) {
			if (!await this.connect())
				return false;
			var startTime = Date.now()
			var interval = setInterval(function(){
				if (timeout && timeout < (Date.now() - startTime))
				{
					clearInterval(interval)
					return resolve(false)
				}
				if (this.replication.lobbyInfo)
				{
					clearInterval(interval)
					return resolve(true)
				}
			}.bind(this), 50)
		}.bind(this))
	}

	async disconnect()
	{
		this.replication.disconnect()
	}

	htmlContent()
	{
		return `<div class="game-canvas">
		<div class="game-window">
			<div class="paddle-left"></div>
			<div class="paddle-right"></div>
			<div class="pong-ball"></div>
		</div>
		<div class="overlay">
		</div>
		</div>
		`
	}
};

window.gameObject = new GameClient();