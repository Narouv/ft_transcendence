
export class Color
{
	constructor(r,g,b,a)
	{
		this.r = this.g = this.b = this.a = 0
		if (r)
			this.r = r
		if (g)
			this.g = g
		if (b)
			this.b = b
		this.a = 1
		if (a)
			this.a = a
	}

	copy()
	{
		return new Color(this.r, this.g, this.b, this.a)
	}

	toRgbCss()
	{
		return `rgb(${this.r},${this.g},${this.b})`
	}

	toRgbaCss()
	{
		return `rgba(${this.r},${this.g},${this.b},${this.r});`
	}

	lerp(goal, delta)
	{
		this.r = this.r + (goal.r - this.r) * delta
		this.g = this.g + (goal.g - this.g) * delta
		this.b = this.b + (goal.b - this.b) * delta
		this.a = this.a + (goal.a - this.a) * delta
	}
};