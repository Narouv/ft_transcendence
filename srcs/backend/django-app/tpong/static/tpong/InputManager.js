
class InputManager
{
	constructor()
	{
		this.keysDown = {};
		this.mouseState = {
			lmb: false,
			rmb: false,
			mmb: false,
		}
		this.onKeyDown = null;
		this.onKeyUp = null;
		this.preventAction = {};
		window.addEventListener('keydown' , this.handleKeyDown.bind(this));
		window.addEventListener('keyup' , this.handleKeyUp.bind(this));
	}

	registerKeyUp(fn)
	{
		this.onKeyUp = fn;
	}

	registerKeyDown(fn)
	{
		this.onKeyDown = fn;
	}

	unregister()
	{
		this.onKeyDown = null
		this.onKeyUp = null
	}

	handleKeyDown(event)
	{
		if (this.preventAction[event.code])
			event.preventDefault()
		this.keysDown[event.code] = true;
		if (this.onKeyDown)
			this.onKeyDown(event.code)
	}

	handleKeyUp(event)
	{
		if (this.preventAction[event.code])
			event.preventDefault()
		this.keysDown[event.code] = false;
		if (this.onKeyUp)
			this.onKeyUp(event.code)
	}
};

export default new InputManager();