import { vec2 } from "./vec2.js";

export class Util
{
	static getGameWindowHtmlObject(num = 0)
	{
		const windows = document.getElementsByClassName('game-window');
		
		if (windows.length)
			return windows[num];
		throw "No game-window element!";
	}

	static getOverlayHtmlObject(num = 0)
	{
		const overlays = document.getElementsByClassName('overlay');
		
		if (overlays.length)
			return overlays[num];
		throw "No overlay element!";
	}

	static getPaddleHtmlObject(side, num = 0)
	{
		const paddles = document.getElementsByClassName('paddle-' + side);
	
		if (paddles.length)
			return paddles[num];
		throw "No paddle-" + side + " element!";
	}

	static getBallHtmlObject(num = 0)
	{
		const balls = document.getElementsByClassName('pong-ball');
	
		if (balls.length)
			return balls[num];
		throw "No pong-ball element!";
	}

	static getDimensionsVec2(obj)
	{
		var boundingBox = obj.getBoundingClientRect();
		
		return new vec2(boundingBox.width, boundingBox.height);
	}

	static lerp (start, end, amt){
		return (1-amt)*start+amt*end
	}
}
