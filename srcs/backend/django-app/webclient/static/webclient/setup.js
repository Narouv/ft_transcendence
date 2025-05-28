import { api } from "/static/api/js/request.js"

function addScript( src, type='module', onload=null) {
	return new Promise((resolve) => {
		var s = document.createElement( 'script' );
		s.src = src;
		s.type = type;
		s.async = true
		const el = document.getElementsByTagName('script')[0]
		el.parentNode.insertBefore(s, el)
		s.addEventListener('load', () => {
			if (onload)
				onload()
			resolve()
		})
	})
}


window.ft_log = function(...args){
	var loggingEnabled = false
	
	if (loggingEnabled)
		console.log(...args)
}

window.api = api

addScript("/static/tpong/GameClient.js", "module").then(()=>{
    if (window.viewManager && window.viewManager.currentView() == "pong")
        window.viewManager.onLoad()
});
await addScript("/static/webclient/pong.js", "module");
await addScript("/static/webclient/friends.js", "module");
await addScript("/static/webclient/gameselection.js", "module");
await addScript("/static/webclient/game-active.js", "module");
await addScript("/static/webclient/view-manager.js", "module");
await addScript("/static/webclient/login.js", "module");
await addScript("/static/webclient/navbar.js", "module");
await addScript("/static/webclient/settings.js", "module");
await addScript("/static/thirdParty/qrcode.min.js", "text/javascript");



