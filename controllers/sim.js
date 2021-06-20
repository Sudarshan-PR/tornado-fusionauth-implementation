perms = false;
  url = "http://localhost:8000/getPermissions";
  data = JSON.stringify({
		'username': username,
    'role': role
  });
  
	var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      // Typical action to be performed when the document is ready:
      perms = xhttp.responseText;
    }
    else{
			console.error("Request error (Else block)");
    }
  };
  
  xhttp.onerror = function() {
		console.error("Error in request to get role permissions! ");
  };
  xhttp.open("POST", url, true);
  xhttp.send(data);
  
  if(perms){
    jwt.permissions = perms;
  }
  
  console.info("User: " + user.preferred_username);
  console.info("Permissions: " + JSON.stringify(perms));
  //console.log(JSON.stringify(user, null, ' '));
	