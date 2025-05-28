import { vec2 } from "./vec2.js";
import { Paddle } from "./Paddle.js";
import { PongBall } from "./PongBall.js";
import collisionManager from "./CollisionManager.js";
import { Overlay } from "./GUI.js"

export class GObjMngr
{
	constructor() {
		let paddleSize = new vec2(0.03, 0.2);
		this.paddles = {
			left: new Paddle('left', paddleSize),
			right: new Paddle('right', paddleSize)
		};
		this.pongBall = new PongBall(0.01);
		this.overlay = new Overlay();
		collisionManager.addCollidableRect(new vec2(), new vec2(1), true, this.onRectCollision.bind(this), {type: "border"});
	}

	onRectCollision(collision, obj)
	{
		//if (collision.side == 'left' || collision.side == 'right')
		//{
		//	alert("Game Over!");
		//	
		//	this.pongBall.ballNormal = new vec2(0.5, 0.5);
		//	this.pongBall.velocityNormal = new vec2(collision == 'left' ? 0.3 : -0.3, 0.21)
		//}
	}

	runSimulation(delta)
	{
		this.pongBall.simulate(delta);
		this.paddles.left.simulate(delta);
		this.paddles.right.simulate(delta);
		collisionManager.runCollision(delta);
	}

	syncDOM()
	{
		this.pongBall.syncDOM();
		this.paddles.left.syncDOM();
		this.paddles.right.syncDOM();
		this.overlay.syncDOM();
	}
};

