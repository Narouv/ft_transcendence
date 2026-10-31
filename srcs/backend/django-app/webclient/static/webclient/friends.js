import { api } from "/static/js/request.js";

class FriendManager
{
    constructor()
    {

    }

    createFriendListElement(friend)
    {
        const listItem = document.createElement("li");
        listItem.classList.add("list-group-item", "d-flex", "justify-content-between", "align-items-center");

        const statusTag = document.createElement("span");
        statusTag.textContent = friend.online != 0 ? "Online" : "Offline";
        statusTag.style.color = friend.online != 0 ? "green" : "gray";
        statusTag.classList.add("badge", friend.online ? "badge-success" : "badge-secondary");

        const nameTag = document.createElement("span");
        nameTag.textContent = friend.username;
        nameTag.classList.add("text-truncate")
        nameTag.style.maxWidth = "100px"
        nameTag.style.overflowX = "hidden"

        const xbutton = document.createElement("button");
        xbutton.type = "button"
        xbutton.classList.add("btn",  "btn-outline-danger", "btn-sm")
        xbutton.textContent = "X"
        xbutton.style.marginLeft = "10px"
        xbutton.setAttribute("data-bs-target-user", friend.username)
        xbutton.setAttribute("data-bs-toggle", "modal")
        xbutton.setAttribute("data-bs-target","#deleteFriendModal")

        statusTag.appendChild(xbutton);
        listItem.appendChild(nameTag);
        listItem.appendChild(statusTag);
        return listItem
    }

    createInFriendRequestElement(request)
    {
        const listItem = document.createElement("li");
        listItem.classList.add("list-group-item", "d-flex", "justify-content-between", "align-items-center");

        const statusTag = document.createElement("span");
        statusTag.textContent = "Pending";
        statusTag.style.color = "gray";
        statusTag.classList.add("badge", "badge-secondary");

        const nameTag = document.createElement("span");
        nameTag.textContent = request.sender.username;
        nameTag.classList.add("text-truncate")
        nameTag.style.maxWidth = "100px"
        nameTag.style.overflowX = "hidden"

        const xbutton = document.createElement("button");
        xbutton.type = "button"
        xbutton.classList.add("btn",  "btn-danger", "btn-sm")
        xbutton.textContent = "X"
        xbutton.addEventListener("click", function(){
            this.declineFriendRequest(request.id)
        }.bind(this))

        const okButton = document.createElement("button");
        okButton.type = "button"
        okButton.classList.add("btn",  "btn-success", "btn-sm")
        okButton.textContent = "✓"
        okButton.addEventListener("click", function(){
            this.acceptFriendRequest(request.id)
        }.bind(this))
        
        var contain = document.createElement("div")
        contain.classList.add("btn-group")
        contain.appendChild(xbutton);
        contain.appendChild(okButton);
        listItem.appendChild(nameTag);
        listItem.appendChild(statusTag);
        listItem.appendChild(contain);
        return listItem
    }

    createOutFriendRequestElement(request)
    {
        const listItem = document.createElement("li");
        listItem.classList.add("list-group-item", "d-flex", "justify-content-between", "align-items-center");

        const statusTag = document.createElement("span");
        statusTag.textContent = "Pending";
        statusTag.style.color = "gray";
        statusTag.classList.add("badge", "badge-secondary");

        const nameTag = document.createElement("span");
        nameTag.textContent = request.receiver.username;
        nameTag.classList.add("text-truncate")
        nameTag.style.maxWidth = "100px"
        nameTag.style.overflowX = "hidden"

        const xbutton = document.createElement("button");
        xbutton.type = "button"
        xbutton.classList.add("btn",  "btn-danger", "btn-sm")
        xbutton.textContent = "X"
        xbutton.style.marginLeft = "10px"
        xbutton.addEventListener("click", function(){
            this.deleteFriendRequest(request.id)
        }.bind(this))

        listItem.appendChild(nameTag);
        listItem.appendChild(statusTag);
        listItem.appendChild(xbutton);
        return listItem
    }

    async getFriends()
    {
        var response = await api.get("/api/user/friends/")
        if (response.success)
            return response.data
        return false;
    }

    async getFriendRequests()
    {
        var response = await api.get("/api/user/friends/request/")
        if (response.success)
            return response.data
        return false; 
    }

    async declineFriendRequest(id)
    {
        var response = await api.request("PATCH", "/api/user/friends/request/", {action: "decline", id: id})
        this.onSwitch(this.getRequestPage())
    }

    async acceptFriendRequest(id)
    {
        var response = await api.request("PATCH", "/api/user/friends/request/", {action: "accept", id: id})
        this.onSwitch(this.getRequestPage())
    }

    async unfriendUser(username)
    {
        var response = await api.request("DELETE", "/api/user/friends/", {username: username})
        this.onSwitch(this.getRequestPage())
    }

    async deleteFriendRequest(id)
    {
        var response = await api.request("DELETE", "/api/user/friends/request/", {id: id})
        this.onSwitch(this.getRequestPage())
    }

    getRequestPage()
    {
        var btn1 = document.getElementById("btnradio1")
        var btn2 = document.getElementById("btnradio2")
        if (btn1.checked)
            return 0
        if (btn2.checked)
            return 1
        return -1
    }   

    async loadFriendRequestPage()
    {
        var requests = await this.getFriendRequests()
        const upperList = document.getElementById("upperList");
        const lowerList = document.getElementById("lowerList");

        if (!requests)
            return false
        upperList.innerHTML = ""
        lowerList.innerHTML = ""
        for (var i = 0; i < requests.in.length; i++)
        {
            var obj = this.createInFriendRequestElement(requests.in[i])
            
	        upperList.appendChild(obj);
        }
        
        for (var i = 0; i < requests.out.length; i++)
        {
            var obj = this.createOutFriendRequestElement(requests.out[i])
            
	        lowerList.appendChild(obj);
        }
    }

    async loadFriendPage()
    {
        const friends = await this.getFriends()
        const upperList = document.getElementById("upperList");
        const lowerList = document.getElementById("lowerList");
        
        if (!friends)
            return false
        upperList.innerHTML = ""
        lowerList.innerHTML = ""
        for (const num in friends)
        {
            var obj = this.createFriendListElement(friends[num])
            
	        upperList.appendChild(obj);
        }
    }

    async onSwitch(id)
    {
        if (id == 0)
            this.loadFriendPage()
        if (id == 1)
            this.loadFriendRequestPage()
    }

    async onAddFriend()
    {
        var feedback = document.getElementById("add-user-feedback")
        var username = document.getElementById("add-friend-username")
        var response = null
        if (username.value)
            response = await api.post("/api/user/friends/request/", { username: username.value })
        else
            response = {success:false, error: "No username!"}
        username.classList.remove("is-valid")
        username.classList.remove("is-invalid")
        feedback.classList.remove("valid-feedback")
        feedback.classList.remove("invalid-feedback")
        if (response.success)
        {
            username.classList.add("is-valid")
            feedback.classList.add("valid-feedback")
        }
        else
        {
            username.classList.add("is-invalid")
            feedback.classList.add("invalid-feedback")
            if (response.error)
                feedback.innerText = response.error
            else        
                feedback.innerText = "Error sending request!"
        }
        

        if (this.getRequestPage())
        {
            this.onSwitch(1)
        }
    }

    loadModal()
    {
        let deleteFriendModal = document.getElementById("deleteFriendModal")
        let unfriendButton = deleteFriendModal.querySelector('.modal-footer .btn-danger')
        deleteFriendModal.addEventListener("show.bs.modal", function(event){
            const button = event.relatedTarget
            const username = button.getAttribute('data-bs-target-user')
            var modalTitle = deleteFriendModal.querySelector('.modal-title')
            var modalBodyText = deleteFriendModal.querySelector('#delete-friend-modal-text')

            unfriendButton.setAttribute("target-user", username)
            modalTitle.innerText = `Delete friend '${username}'`;
            modalBodyText.innerHTML = `You are about to unfriend '${username}'`;
        }.bind(this))
        unfriendButton.addEventListener("click", function(event){
            this.unfriendUser(unfriendButton.getAttribute("target-user"))
            unfriendButton.removeAttribute("target-user")
        }.bind(this))
    }

    load()
    {   
        var id = this.getRequestPage()
        if (id == 0)
            this.loadFriendPage()
        if (id == 1)
            this.loadFriendRequestPage()
        document.getElementById("btnradio1").addEventListener("change", function(){
            this.onSwitch(0)
        }.bind(this))
        document.getElementById("btnradio2").addEventListener("change", function(){
            this.onSwitch(1)
        }.bind(this))
        document.getElementById("add-friend").addEventListener("click", function(){
            this.onAddFriend()
        }.bind(this))
        this.loadModal()
    }
};

window.friendManager = new FriendManager()