import "/static/webclient/setup.js"
import { NavbarManager } from '/static/webclient/navbar.js';

export class ViewManager
{
	constructor()
	{
		this.navbarBox = document.getElementById("navbar");
		this.contentBox = document.getElementById("content");
		this.currentViewLoading = ""
		this.views = {};


		this.loadQueue = []
		this.isExecutingQueue = false
		this.queuesExecuted = 0

		this.views["login"] = 		{ perm: 0,  onLoad: null }
		this.views["register"] = 	{ perm: 0,  onLoad: null }
		this.views["home"] = 		{ perm: 1,  onLoad: () => {
			if (window.gameObject && window.target)
				gameObject.startEngine()
		}}
		this.views["game-active"] = { perm: 2,  onLoad: () => {
			if (window.gameObject)
			{
				gameManager.onViewLoad()
			}
		}}
		this.views["gameselection"] = { perm: 2,  onLoad: async () => {
			if (window.gameObject)
			{
				if (await gameModeManager.getActiveLobby())
					gameManager.loadActiveView()
			}
		}}
		this.views["profile"] = 	{ perm: 2,  onLoad: () => {
			window.friendManager.load()
		}}
		this.views["settings"] = 	{ perm: 2,  onLoad: null}
		this.views["match-result"] = 	{ perm: 2,   onLoad: () => {
		}}
		this.views["setup-2FA"] = 	{ perm: 2,   onLoad: () => {
			profileSettings.start2faSetup()
		}}
		window.addEventListener("popstate", this.historyManager);
	}

	async executeQueue(nr)
	{
		this.isExecutingQueue = true
		if (this.loadQueue.length)
		{
			var job = this.loadQueue.shift()
			await this.getPage( ...job.parameter )
			job.resolve()
		}
		else
			return
		await this.executeQueue(nr)
		ft_log("[" + new Date().toISOString() + "] Finished queue execution (" + nr + ")")
		this.isExecutingQueue = false
	}

	queueView(page, args, addToHistory = true)
	{
		return new Promise(async function(promise){
			var queueObj = {
				parameter: [page, args, addToHistory],
				resolve: promise
			}
			ft_log("[" + new Date().toISOString() + "] Queued view " + page)
			this.loadQueue.push(queueObj)
			if (!this.isExecutingQueue)
			{
				ft_log("[" + new Date().toISOString() + "] Starting queue execution (" + this.queuesExecuted + ")")
				this.executeQueue(this.queuesExecuted)
				this.queuesExecuted += 1
			}
		}.bind(this))
	}

	async getPage(page, args, addToHistory = true)
	{
		if (page === "")
			page = "home";

		var view = this.views[page]
		var authenticated = await api.verifyAuthenticated()

		if (((view && view.perm == 0) && authenticated) ||
			((!view && !authenticated) || (!authenticated && (view && view.perm > 1))))
		{
			page = "home";
			view = this.views[page]
		}
		this.currentViewLoading = page
		var viewData = await api.post(`/views/${page}/`, { args: args }, { type: "text" })

		if (window.gameObject && page != "pong")
			window.gameObject.stopEngine()

		this.contentBox.innerHTML = viewData

		if (addToHistory)
			window.history.pushState({'page': page }, "", `#${page}`);
		if (view)
		{
			// ft_log("Executing callback for " + page)
			if (view.onLoad)
				view.onLoad()
		}
		// ft_log("Finished loading view " + page)
		this.currentViewLoading = "NONE"
		return;
	}

	async getNavbar()
	{
		this.navbarBox.innerHTML = await api.post("/views/navbar/", null,  { type: "text" });
	}

	historyManager(s)
	{
		if (s.state != null)
		{
			viewManager.getPage(s.state.page, null, false)
		}
	}

	currentView()
	{
		return window.location.hash.split('#').pop()
	}

	onLoad() {
		this.getNavbar().then(() => {
			const navbarElement = document.getElementById("MainNavbar-Itemlist");
			const navbarManager = new NavbarManager(navbarElement);

			navbarManager.onResize();
			this.getPage(this.currentView());
		});
	}
}

window.viewManager = new ViewManager()

document.addEventListener('DOMContentLoaded', () => {
	window.viewManager.onLoad()
});

if (document.readyState != 'loading')
	window.viewManager.onLoad()

