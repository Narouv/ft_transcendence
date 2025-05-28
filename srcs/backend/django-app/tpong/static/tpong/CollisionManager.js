import { vec2 } from "./vec2.js";

class CollisionManager
{
	constructor()
	{
		this.collidableObjects = [];
	}

	createUID()
	{
		var str = "";
		var arr = window.crypto.getRandomValues(new Uint8Array(16));
		for (const num of arr)
			str += num.toString(16);
		return str;
	}

	addCollidableRect(position, size, bInside, onCollision, obj=null)
	{
		const uid = this.createUID();
		this.collidableObjects.push({
			uid: uid,
			type: 'rect',
			pos: position,
			size: size,
			onCollision: onCollision,
			insideCollision: bInside,
			obj: obj
		});
		return uid;
	}

	addCollidableCircle(position, radius, onCollision, obj=null)
	{
		const uid = this.createUID();
		this.collidableObjects.push({
			uid: uid,
			type: 'circle',
			pos: position,
			radius: radius,
			onCollision: onCollision,
			obj: obj
		});
		return uid;
	}

	updateCollidableObject(uid, position)
	{
		var objIdx = this.collidableObjects.findIndex((element) => element.uid == uid);
		if (objIdx < 0)
			throw "No collidable object to edit with UID: " + uid;
		this.collidableObjects[objIdx].pos = position;
	}

	removeCollidableObject(uid)
	{
		var objIdx = this.collidableObjects.findIndex((element) => element.uid == uid);
		if (objIdx < 0)
			throw "No collidable object to remove with UID: " + uid;
		this.collidableObjects.splice(objIdx, 1);
	}

	checkCollisionRectRect(rect1, rect2)
	{
		var diff1 = rect2.pos.subtract(new vec2(rect1.pos.x + rect1.size.x, rect1.pos.y + rect1.size.y))
		var diff2 = rect1.pos.subtract(new vec2(rect2.pos.x + rect2.size.x, rect2.pos.y + rect2.size.y))
		if ((diff1.x > 0 || diff1.y > 0)
			|| (diff2.x > 0 || diff2.y > 0))
			return false;
		return true;
	}

	checkCollisionCircleRect(circle, rect)
	{
		var collisionSide = undefined;
		if (rect.insideCollision)
		{
			if (circle.pos.x - circle.radius <= rect.pos.x)
				collisionSide = 'left';
			if (circle.pos.x + circle.radius >= rect.pos.x + rect.size.x)
				collisionSide = 'right';
			if (circle.pos.y - circle.radius <= rect.pos.y)
				collisionSide = 'top';
			if (circle.pos.y + circle.radius >= rect.pos.y + rect.size.y)
				collisionSide = 'bottom';
			return {
				collide: collisionSide ? true : false,
				side: collisionSide,
				clipPos: new vec2()
			}
		}
	
		var closestPoint = circle.pos.copy();
		if (circle.pos.x < rect.pos.x)
		{
			collisionSide = 'right'
			closestPoint.x = rect.pos.x;
		}
		else if (circle.pos.x > rect.pos.x + rect.size.x)
		{
			collisionSide = 'left'
			closestPoint.x = rect.pos.x + rect.size.x;
		}
		if (circle.pos.y < rect.pos.y)
		{
			collisionSide = 'bottom'
			closestPoint.y = rect.pos.y;
		}
		else if (circle.pos.y > rect.pos.y + rect.size.y)
		{
			collisionSide = 'top'
			closestPoint.y = rect.pos.y + rect.size.y;
		}
	
		
		var dist = circle.pos.distTo(closestPoint)
		if (dist < circle.radius)
		{
			var clipPos = new vec2();

// Clipping for even better collision - Still buggy and maybe not needed
			if (circle.pos.x < rect.pos.x + (rect.size.x / 2))
			{
				clipPos.x = rect.pos.x - circle.radius;
			} else if (circle.pos.x >= rect.pos.x + (rect.size.x / 2))
				clipPos.x = rect.pos.x + rect.size.x + circle.radius;
			if (circle.pos.y < rect.pos.y + (rect.size.y / 2))
				clipPos.y = rect.pos.y - (circle.radius );
			else if (circle.pos.y >= rect.pos.y + (rect.size.y / 2))
				clipPos.y = rect.pos.y + rect.size.y + circle.radius;
			if (collisionSide == 'top' || collisionSide == 'bottom')
				clipPos.x = 0;
			else
				clipPos.y = 0;
			return {
				collide: true,
				side: collisionSide,
				clipPos: clipPos
			}
		}
		return {
			collide: false,
		}
	}

	checkCollision(obj1, obj2)
	{
		if (obj1.type == 'rect'
			&& obj2.type == 'circle')
			return this.checkCollisionCircleRect(obj2, obj1);
		if (obj1.type == 'circle'
			&& obj2.type == 'rect')
			return this.checkCollisionCircleRect(obj1, obj2);
		return false;
	}

	runCollision(delta)
	{
		var collisionsHappened = [];
		for (const collidableObject of this.collidableObjects)
		{
			for (const collidableObjectToCheck of this.collidableObjects)
			{
				if (collidableObject.uid == collidableObjectToCheck.uid)
					continue;
				if (collisionsHappened.find((element) => {
					var found = 0;
					for (const collidedObj of element)
					{
						if (collidedObj.uid == collidableObject.uid
							|| collidedObj.uid == collidableObjectToCheck.uid)
							found++;
					}
					return found == 2;
				}))
					continue;
				var collision = this.checkCollision(collidableObject, collidableObjectToCheck);
				if (collision.collide)
				{
					if (collidableObject.onCollision)
						collidableObject.onCollision(collision, collidableObjectToCheck.obj);
					if (collidableObjectToCheck.onCollision)
						collidableObjectToCheck.onCollision(collision, collidableObject.obj);
					collisionsHappened.push([collidableObject, collidableObjectToCheck])
				}
			}
		}
	}
};

export default new CollisionManager();