import { Util } from "./Util.js";
import { vec2 } from "./vec2.js";
import collisionManager from "./CollisionManager.js";
import { Color } from "./Color.js";


export class PongBall
{
	constructor(radius)
	{
		this.type = "ball"
		this.radiusNormal = radius;
		this.ballNormal = new vec2(0.5, 0.5);
		this.serverBallNormal = new vec2(0.5, 0.5);
		this.velocityNormal = new vec2()
		this.cuid = collisionManager.addCollidableCircle(new vec2(), this.radiusNormal, this.onCollision.bind(this), this);
		this.color = new Color(255, 255, 255, 1)
	}

	syncDOM()
	{
		var pos = this.ballNormal.subtract(new vec2(this.radiusNormal));
		var ball = Util.getBallHtmlObject();
		const boundingBox = Util.getGameWindowHtmlObject().getBoundingClientRect();
		var aspectRatioW = boundingBox.width / boundingBox.height
		
		pos = pos.multiply(new vec2(boundingBox.width, boundingBox.height - ((this.radiusNormal * 2) * boundingBox.height) * (aspectRatioW - 1)));
		ball.style.backgroundColor = this.color.toRgbCss()
		ball.style.height = ((this.radiusNormal * 2) * boundingBox.height) * aspectRatioW + 'px';
		ball.style.width = ((this.radiusNormal * 2) * boundingBox.width) + 'px';
		ball.style.position = 'absolute';
		ball.style.left = pos.x + 'px';
		ball.style.top = pos.y + 'px';
	}

	reset()
	{
		this.ballNormal = new vec2(0.5, 0.5);
		this.velocityNormal = new vec2(0.0, 0.0);
	}

	simulate(delta)
	{
		//this.velocityNormal.y += 0.0981 * delta;
		this.serverBallNormal = this.serverBallNormal.add(this.velocityNormal.multiply(new vec2(delta)));
		this.serverBallNormal = this.serverBallNormal.clamp(new vec2(1 - this.radiusNormal), new vec2(this.radiusNormal));
		this.ballNormal.lerp(this.serverBallNormal, delta * 40)
	
		//this.ballNormal = this.ballNormal.add(this.velocityNormal.multiply(new vec2(delta)));
		this.ballNormal = this.ballNormal.clamp(new vec2(1 - this.radiusNormal), new vec2(this.radiusNormal));
		collisionManager.updateCollidableObject(this.cuid, this.ballNormal);
		this.color.lerp(new Color(255, 255, 255, 1), delta)
	}

	onCollision(collision, obj)
	{
		if (collision.clipPos.x)
			this.ballNormal.x = collision.clipPos.x //* (1 + this.radiusNormal);
		if (collision.clipPos.y)
			this.ballNormal.y = collision.clipPos.y //* (1 + this.radiusNormal);
		this.ballNormal = this.ballNormal.clamp(new vec2(1 - this.radiusNormal), new vec2(this.radiusNormal));
		if (collision.side == 'left' && this.velocityNormal.x < 0
			|| collision.side == 'right' && this.velocityNormal.x > 0)
			this.velocityNormal.x *= -1;
		if (collision.side == 'top' && this.velocityNormal.y < 0
			|| collision.side == 'bottom' && this.velocityNormal.y > 0)
			this.velocityNormal.y *= -1;
		if (obj.type == "paddle")
		{
			var diff = this.ballNormal.y - (obj.getWindowNormal().y + obj.sizeNormal.y * 0.5)
			var angle = diff * (90 / obj.sizeNormal.y)
			var newVel = new vec2(1,0).rotate(angle)
			if (this.velocityNormal.x < 0)
				newVel.x *= -1
			this.velocityNormal = newVel.multiply(new vec2(this.velocityNormal.length()))
			if (this.velocityNormal.length() < 0.8)
				this.velocityNormal.multiply(new vec2(1.1))
		}
	}
}

