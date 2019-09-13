$(document).ready(function() {
  Avai_Pin();
  Used_Pin();
  Avai_Net();
  Avai_num();
      // Get the form fields and hidden div
  var checkbox = $("#PProtected");
  var hidden = $("#inputPassword");
      //for mqtt settings
  var checkbox2 = $("#mqtt_set");
  var hidden2 = $("#mqtt_settings");

  
  // Hide the fields.
  // Use JS to do this in case the user doesn't have JS 
  // enabled.
  hidden.hide();
  hidden2.hide();

  var Devices = $("#select-device");
  var PINS_Add = $("#echo-select");
  var RGBpin = $("#RGB-select");
  PINS_Add.hide();
  RGBpin.hide();

  Devices.change(function(){
    if (Devices.val() == "Ultrason"){

      PINS_Add.show();
      RGBpin.hide();
      document.getElementById("echo").innerHTML = "Choose the Pin(echo):"
      document.getElementById("echo_op").innerHTML = "Choose the Pin(echo):"

      document.getElementById("select-origin").innerHTML = "Choose the Pin:"
      document.getElementById("origin-select").innerHTML = "Choose the Pin:"
    }else if(Devices.val() == "RGB"){
      PINS_Add.show();
      RGBpin.show();
      document.getElementById("echo").innerHTML = "Choose the Pin(Green):"
      document.getElementById("echo_op").innerHTML = "Choose the Pin(Green):"

      document.getElementById("select-origin").innerHTML = "Choose the Pin(Red):"
      document.getElementById("origin-select").innerHTML = "Choose the Pin(Red):"


    }else{
      RGBpin.hide();
      PINS_Add.hide();
      document.getElementById("echo").innerHTML = "Choose the Pin(echo):"
      document.getElementById("echo_op").innerHTML = "Choose the Pin(echo):"

      document.getElementById("select-origin").innerHTML = "Choose the Pin:"
      document.getElementById("origin-select").innerHTML = "Choose the Pin:"
    }
  })

  // Setup an event listener for when the state of the 
  // checkbox changes.
  checkbox.change(function() {
    // Check to see if the checkbox is checked.
    // If not, hide the fields.
    if (checkbox.is(':checked')) {
      // Show the hidden fields.
      hidden.show();
    } else {
      // Make sure that the hidden fields are indeed
      // hidden.
      hidden.hide();

    }
  });
  checkbox2.change(function() {
    // Check to see if the checkbox is checked.
    // If not, hide the fields.
    if (checkbox2.is(':checked')) {
      // Show the hidden fields.
      hidden2.show();
    } else {
      // Make sure that the hidden fields are indeed
      // hidden.
      hidden2.hide();

    }
  });
});
//GET Availble Pins
function Avai_Pin(){
  var xhttp = new XMLHttpRequest();

xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {

      var list = JSON.parse(xhttp.responseText);
      //reinit the pins list 
      $("#select-pins").empty();
      $("#select-pins-echo").empty();
      $("#select-RGB-B").empty();
      $("#select-pins").append("<option id='origin-select' value='' disabled selected>Choose the Pin</option>");
      $("#select-pins-echo").append("<option id='echo_op' value='' disabled selected>Choose the Pin(for echo)</option>");
      $("#select-RGB-B").append("<option value='' disabled selected>Choose the Pin(Blue)</option>");
      for (var i = 0; i < list.length; i++) {
    
          $("#select-pins").append("<option value="+list[i]+">"+list[i]+"</option>");
          $("#select-pins-echo").append("<option value="+list[i]+">"+list[i]+"</option>");
          $("#select-RGB-B").append("<option value="+list[i]+">"+list[i]+"</option>");
        }
    }
};
xhttp.open("GET", "/pins", true);
xhttp.send();
}

// func to check if the arg is a number
function isNum(arg) {
  return typeof arg === 'number';
}


//GET All used pins
function Used_Pin(){

    var xhttp1 = new XMLHttpRequest();
    xhttp1.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      var list = JSON.parse(xhttp1.responseText);

      //reinit pins list
      $("#del-pins").empty();

      for (var i = 0; i < list.length; i++) {

          //write values of pins on the options unless it's a name of device then write it in a way so iy can't be selected
          if(isNum(list[i])){   

          $("#del-pins").append("<option value="+list[i]+">"+list[i]+"</option>");
          $("#del-pins-echo").append("<option value="+list[i]+">"+list[i]+"</option>");
        }else if(typeof list[i] == "object"){

          $("#del-pins").append("<option value='"+list[i]+"' >"+list[i]+"</option>");
        }else{
          $("#del-pins").append("<option value='' disabled selected>"+list[i]+"</option>");
        }


        }
        //so when the list updates the value written is "Choose the pin"
              $("#del-pins").prepend("<option value='' disabled selected>Choose the Pin</option>");
              $("#del-pins-echo").prepend("<option value='' disabled selected>Choose the Pin</option>");
    }
};
xhttp1.open("GET", "/Delpins", true);
xhttp1.send();
}

//Phone number
function Avai_num(){

    var xhttp2 = new XMLHttpRequest();
    xhttp2.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      var list = JSON.parse(xhttp2.responseText);

      //reinit both select-wifi and del-wifi lists
      $("#del-phone").empty();
      $("#del-phone").append('<option value="" disabled selected>Choose phone number:</option>');
      for (var i = 0; i < list.length; i++) {
          $("#del-phone").append("<option value="+list[i]+">"+list[i]+"</option>");
        }
    }
};
xhttp2.open("GET", "/phone", true);
xhttp2.send();
 }

//GET Availble Networks
function Avai_Net(){

    var xhttp2 = new XMLHttpRequest();
    xhttp2.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      
      var list = JSON.parse(xhttp2.responseText);
      //reinit both select-wifi and del-wifi lists
      $("#select-Wifi").empty();
      $("#Del-Wifi").empty();
      $("#Del-Wifi").append("<option value='' disabled selected>Remove network</option>");
      $("#select-Wifi").append("<option value='' disabled selected>Choose your network</option>");
      for (var i = 0; i < list.length; i++) {
    
          $("#select-Wifi").append("<option value="+list[i]+">"+list[i]+"</option>");
          $("#Del-Wifi").append("<option value="+list[i]+">"+list[i]+"</option>");
        }
    }
};
xhttp2.open("GET", "/wifis", true);
xhttp2.send();
 }

//this tell to the esp the network to use after normal startup
function Submit_usedNet(){
  
  Wifi = document.getElementById("select-Wifi").value
  var xhttp = new XMLHttpRequest();
  xhttp.open('POST', 'http://' + window.location.hostname + '/Used_Net', true);
  xhttp.setRequestHeader('Content-type', 'application/json')

  xhttp.send(Wifi)
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      Avai_Net();
  document.getElementById("result_net").innerHTML = '<p id="result_net" style="color:#74FF00">'+xhttp.responseText+'</p>'
    }
  };      

}
// this func delete wifi from configuration file(or actually tell microWebSrv in the backend to do it)
function Del_Net(){
  
  Wifi = document.getElementById("Del-Wifi").value

  var xhttp = new XMLHttpRequest();
  xhttp.open('POST', 'http://' + window.location.hostname + '/Del_Wifi', true);
  xhttp.setRequestHeader('Content-type', 'application/json')
  xhttp.send(Wifi)

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
         //print the result of the submiting (error/succesfull)  
  document.getElementById("result_net").innerHTML = '<p id="result_net" style="color:#74FF00">'+xhttp.responseText+'</p>'
  //reinit availbal-networks list 
  Avai_Net();
    }
  };      

}
// Delete Device after selecting Device and pin
function del_Dev(){
  
  device = document.getElementById("del-device").value
  Pin = document.getElementById("del-pins").value.split(",")

  if (typeof Pin == "number" ){
  data = '{"Device_type":"'+device+'","device_pin":"'+Pin+'"}'
  }else if (device == "Ultrason"){
    data = '{"Device_type":"'+device +'","device_pin":"'+Pin[0]+'","device_pin_echo":"'+Pin[1]+'"}'
  }else{
    data = '{"Device_type":"'+device +'","R":"'+Pin[0]+'","G":"'+Pin[1]+'","B":"'+Pin[2]+'"}'
  }
  
  var xhttp = new XMLHttpRequest();
  xhttp.open('POST', 'http://' + window.location.hostname + '/DelDevice', true);
  xhttp.setRequestHeader('Content-type', 'applicationl/json')
  xhttp.send(data)

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
       //print the result of the submiting (only succesfull) :p 
  document.getElementById("result_del_device").innerHTML = '<p id="result_del_device" style="color:#74FF00">'+xhttp.responseText+'</p>'
    //reinit pins list
    Avai_Pin();
    Used_Pin();
    }else{
      //this time I checked error by checking response code (if 200) 
          document.getElementById("result_del_device").innerHTML = '<p id="result_del_device" style="color:#FF0000">Error:Wrong Device/Pin!!</p>'

    }
  };
}

//add devices
function submit_device(){
  
  device = document.getElementById("select-device").value
  Pin = document.getElementById("select-pins").value
  Pin_echo = document.getElementById("select-pins-echo").value
  Pin_rgb = document.getElementById("select-RGB-B").value
  if ($("#select-device").val() == "Ultrason" ){
  data = '{"Device_type":"'+device+'","device_pin":"'+Pin+'","device_pin_echo":"'+Pin_echo+'"}'
   }else if($("#select-device").val() == "RGB"){
  data = '{"Device_type":"'+device+'","device_pins":['+Pin+','+Pin_echo+','+Pin_rgb+']}'  
  }else{
  data = '{"Device_type":"'+device+'","device_pin":"'+Pin+'"}' 
  }

  var xhttp = new XMLHttpRequest();
  xhttp.open('POST', 'http://' + window.location.hostname + '/AddDevice', true);
  xhttp.setRequestHeader('Content-type', 'applicationl/json')
  xhttp.send(data)

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
         //print the result of the submiting (error/succesfull)  
  document.getElementById("result_device").innerHTML = '<p id="result_device" '+xhttp.responseText+'</p>'
    //reinit the list of pins
    Avai_Pin();
    Used_Pin();
    }
  };
}

//Adding a new wifi to the conf-file's wifi list
function submit_wifi(){

  ssid = document.getElementById("SSID").value;
  pwd = document.getElementById("inputPassword").value;
  dataa = '{"SSID":"'+ssid+'","Password":"'+pwd+'"}'
  
  var xhttp = new XMLHttpRequest();
  xhttp.open('POST', 'http://' + window.location.hostname + '/wifis', true);
  xhttp.setRequestHeader('Content-type', 'application/json');
  xhttp.send(dataa)

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
    //print the result of the submiting (error/succesfull)  
  document.getElementById("result_wifi").innerHTML = '<p id="result_wifi" style="color:#74FF00">'+xhttp.responseText+'</p>'
   //reinit the availbal-networks list
    Avai_Net();
    }
  };
}
// send signal to reset the device
function reset_device(){
  var xhttp = new XMLHttpRequest();
  xhttp.open('POST', 'http://' + window.location.hostname + '/reset', true);
  xhttp.setRequestHeader('Content-type', 'application/json');
  xhttp.send()

  xhttp.onreadystatechange = function(){
    if(this.readyState == 4 && this.status == 200){
        document.getElementById("reset").innerHTML = "Restarting device..."
      }

  };
}
// submiting phone number
function submit_phone(){

  Phone = document.getElementById("phone_number").value;

  
  var xhttp = new XMLHttpRequest();
  xhttp.open('POST', 'http://' + window.location.hostname + '/phone', true);
  xhttp.setRequestHeader('Content-type', 'application/json');
  xhttp.send(Phone)

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
    //print the result of the submiting (error/succesfull)  
  document.getElementById("result_phone").innerHTML = '<p id="result_phone" style="color:#74FF00">'+xhttp.responseText+'</p>'

    }else{
      document.getElementById("result_phone").innerHTML = '<dont id="result_phone" color="red">'+xhttp.responseText+'</font>'
    }
  };
}
// submiting mqtt settings
function submit_mqtt(){

  user = document.getElementById("mqtt_User").value;
  pwd = document.getElementById("mqtt_Pass").value;
  server = document.getElementById("mqtt_server").value;
  dataa = '{"mqtt_User":"'+user+'","mqtt_Pass":"'+pwd+'","mqtt_server":"'+server+'"}';
  
  var xhttp = new XMLHttpRequest();
  xhttp.open('POST', 'http://' + window.location.hostname + '/mqtt', true);
  xhttp.setRequestHeader('Content-type', 'application/json');
  xhttp.send(dataa)

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
    //print the result of the submiting (error/succesfull)  
  document.getElementById("result_mqtt").innerHTML = '<p id="result_mqtt" style="color:#74FF00">'+xhttp.responseText+'</p>'

    }else{
        document.getElementById("result_mqtt").innerHTML = '<font id="result_mqtt" color="red">'+xhttp.responseText+'</font>'

    }
  };
}

function Del_phone(){
  
  phone = document.getElementById("del-phone").value

  var xhttp = new XMLHttpRequest();
  xhttp.open('POST', 'http://' + window.location.hostname + '/Del_phone', true);
  xhttp.setRequestHeader('Content-type', 'application/json')
  xhttp.send(phone)

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
         //print the result of the submiting (error/succesfull)  
  document.getElementById("result_delphone").innerHTML = '<p id="result_delphone" style="color:#74FF00">'+xhttp.responseText+'</p>'
  //reinit availbal-networks list 
  Avai_num();
    }
  };      

}

