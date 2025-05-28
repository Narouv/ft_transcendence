import { Util } from "./Util.js";
import { vec2 } from "./vec2.js";
import { Color } from "./Color.js";
import InputManager from "./InputManager.js";
import collisionManager from "./CollisionManager.js";

export class Paddle
{
	net =	{
		CONTROLLING:'controlling',
		REPLICATED:'replicated'
	}
	
	constructor(side, size)
	{
		this.type = "paddle"
		this.side = side;
		this.sizeNormal = size;
		this.heightNormal = 0.5;
		this.serverHeightNormal = 0.5;
		this.velocityNormal = 0.0;
		this.maxVelocity = 0.7
		this.cuid = collisionManager.addCollidableRect(this.getWindowNormal(), this.sizeNormal, false, this.onCollision.bind(this), this)
		this.networkingState = this.net.CONTROLLING;
		this.color = this.side == "left" ? new Color(15, 125, 252) : new Color(255, 42, 42)
	}

	getWindowNormal()
	{
		var x = 0;
		if (this.side == 'right')
			x = 1 - this.sizeNormal.x;
		return new vec2(x, this.heightNormal * (1 - this.sizeNormal.y))
	}

	syncDOM()
	{
		var paddle = Util.getPaddleHtmlObject(this.side);
		const windowBoundingBox = Util.getGameWindowHtmlObject().getBoundingClientRect();
		var ballBoundingBox = Util.getBallHtmlObject().getBoundingClientRect();
		var pos = this.getWindowNormal();
		var aspectRatioW = windowBoundingBox.width / windowBoundingBox.height

		var aspectFix = (ballBoundingBox.height * aspectRatioW) - ballBoundingBox.height

		pos = pos.multiply(new vec2(windowBoundingBox.width, windowBoundingBox.height ));
		// pos = pos.add(new vec2(windowBoundingBox.left + document.documentElement.scrollLeft, windowBoundingBox.top + document.documentElement.scrollTop));
		paddle.style.backgroundColor = this.color.toRgbCss()

		paddle.style.width = this.sizeNormal.x * windowBoundingBox.width  + 'px';
		paddle.style.height = this.sizeNormal.y * windowBoundingBox.height + 'px';
		paddle.style.position = 'abolute';
		paddle.style.left = pos.x + 'px';	
		paddle.style.top =  pos.y +'px';
	}

	simulate(delta)
	{
		//if (this.networkingState == this.net.CONTROLLING)
		//	this.processInput();
		this.serverHeightNormal = this.serverHeightNormal + this.velocityNormal * delta;
		this.serverHeightNormal = Math.max(Math.min(this.serverHeightNormal, 1), 0);
		this.heightNormal = Util.lerp(this.heightNormal, this.serverHeightNormal, delta * 10)
		this.heightNormal = Math.max(Math.min(this.heightNormal, 1), 0);
		collisionManager.updateCollidableObject(this.cuid, this.getWindowNormal());
	}

	reset()
	{
		this.heightNormal = 0.5;
		this.velocityNormal = 0.0;
	}

	onCollision(collision, obj)
	{
		if (!obj)
			return
		if (obj.type == "ball")
		{
			obj.color = this.color.copy()
		}
	}

	processInput()
	{
		var velocityNormal = 0.0;
		if (InputManager.keysDown[this.side == 'right' ? 'ArrowUp' : 'KeyW'])
			velocityNormal -= this.maxVelocity;
		if (InputManager.keysDown[this.side == 'right' ? 'ArrowDown' : 'KeyS'])
			velocityNormal += this.maxVelocity;
		if (velocityNormal == 0.0)
			this.velocityNormal *= 0.8;
		else
			this.velocityNormal += (velocityNormal - this.velocityNormal) * 0.2
		//this.velocityNormal = velocityNormal;
		return velocityNormal != 0
	}

	serialize()
	{
		return {
			objName: 'paddle',
			paddleSide: this.side,
			paddleHeight: this.heightNormal,
			paddleVelocity: this.velocityNormal
		}
	}
}