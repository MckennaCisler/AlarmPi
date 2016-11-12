/* main.js
 *
 * All primary javascript for ../index.html
 * in AlarmPi public configuration page.
 *
 * Mckenna Cisler
 * 7.4.2016
 */

// CONSTANTS

CONFIG_HANDLER_URL = "config";
STATE_CHECK_FREQUENCY = 250; // ms
DONE_CHANGING_TIMEOUT = 250; // ms
SUBMIT_CHANGE_DELAY = 2000; // ms

// GLOBAL VARIABLES

// A queue of ready-to-be-sent post requests and their creation times
settingChangeQueue = [];

// timeout object to be used for activating a new settingChangeQueue object after
// the user has finished entering it
doneChangingTimeout = null;

// Saving variable to indicate whether a save request is out
saving = false;

$(document).ready(function () {
	
	// VARIOUS HTML CONFIGURATIONS
	$(".input-popup").popover();
	$("[id^=input-type-]").change(function () {
		// when a type input changes, make sure ONLY the corresponding subtype is visible
		dayOrGlobal = this.id.slice(this.id.lastIndexOf("-") + 1);
		
		soundElement = $("#subtype_sound-select-" + dayOrGlobal);
		pandoraElement = $("#subtype_pandora-select-" + dayOrGlobal)
		
		if (this.value == "sound") {
			soundElement.show();
			pandoraElement.hide();
		} else {
			soundElement.hide();
			pandoraElement.show();
		}
	});
	
	
	// Allow "Save Configuration" button to immediately save all changes
	// Assign all inputs a generic callback for queuing setting changes
	$("#config-save").click(function () {
		// activate all requests (they'll autoremove themselves)
		for (var i = settingChangeQueue.length - 1; i >= 0; i--){
			saving = true;
			$.post(settingChangeQueue[i].settings);
		}
	});
	
	// Assign all inputs a generic callback for queuing setting changes
	$(".setting").change(function () {
		// cancel previous timeout
		window.clearTimeout(doneChangingTimeout);
		
		// set new one to finally submit change request to queue
		doneChangingTimeout = window.setTimeout(addSettingChangeRequest, DONE_CHANGING_TIMEOUT, this);
	});
	
	// periodically call a method to check the status of the changeQueue and inform user
	// based on this
	window.setInterval(periodicStateChecker, STATE_CHECK_FREQUENCY);
	
	// ensure that window is not closed if there is unsaved or saving data)
	// copied from https://developer.mozilla.org/en-US/docs/Web/Events/beforeunload 
	window.addEventListener("beforeunload", function (e) {
		if (settingChangeQueue.length !== 0) {
			var confirmationMessage = "Not all changes have been saved, do you want to discard them?";
		  
			e.returnValue = confirmationMessage;     // Gecko, Thrident, Chrome 34+
			return confirmationMessage;              // Gecko, WebKit, Chrome <34
		}
	});
});

// CREATE METHOD TO SCAN FOR READY posts and send them if ready
function periodicStateChecker() {
	if (settingChangeQueue.length === 0) {
		setStateSaved();
	} else {
		if (saving)
			setStateSaving();
		else
			setStateUnsaved();
	}
}

// CREATE CALLBACK THAT WILL PREPARE A generic POST request to set a setting for a generic setting input (of setting class)
function addSettingChangeRequest(element) {
	var timestamp = new Date();
	
	// get data from element and format correctly for handler
	// quit if nothing present in the element
	var configChanges = {};
	
	var elementID = element.id;

	// get the setting this element is referring to
	var settingName = elementID.slice(elementID.indexOf("-") + 1, elementID.lastIndexOf("-"));
	
	// get the value of the setting in any case
	var settingValue = "";
	if (settingName == "state")
		settingValue = $(element).is(":checked") ? "on" : "off";
	// convert minute measures to seconds
	else if (settingName ==  "time_to_sleep" ||
			 settingName == "max_oversleep" ||
			 settingName == "snooze_time" ||
			 settingName == "activation_timeout")
		settingValue = element.value * 60;
	// convert hour measures to seconds
	else if (settingName == "desired_sleep_time")
		settingValue = element.value * 3600;
	else
		settingValue = element.value;	

	// set the setting if it is not empty (indicating no change)
	if (settingValue.length !== 0) {
		configChanges[settingName] = settingValue;
	} else {
		return;
	}
	
	// determine whether it is a day-based or global setting to compile the final request
	var settingDay = elementID.slice(elementID.lastIndexOf("-") + 1);
	if (settingDay != "global") {
		configChanges.day = settingDay;
	}
	
	requestSettings = {
		url: CONFIG_HANDLER_URL,
		data: configChanges,
		type: "POST",
		success: function () {
			// remove this request from settingChangeQueue upon its return
			removeQueueElement("timestamp", timestamp);
			saving = false;
		}
	};
	
	// remove any other pending changes for this element
	removeQueueElement("element", element);
		
	// send this request in a bit
	var timeout = setTimeout(function() {
		saving = true;
		$.post(requestSettings);
	}, SUBMIT_CHANGE_DELAY);
	
	settingChangeQueue.push({
		settings: requestSettings,
		element: element,
		timestamp: timestamp,
		timeoutID: timeout
	});
}

/**
 * Removes (and cancels the timeouts of) all queue elements for which the given property matches the given match.
 */
function removeQueueElement(property, match) {
	for (var i = 0; i < settingChangeQueue.length; i++) {
		if (settingChangeQueue[i][property] == match) {
			// cancel timeout if active and remove 
			window.clearTimeout(settingChangeQueue[i].timeoutID);
			settingChangeQueue.splice(i, 1);
		}
	}
}

/*
 * Display management methods
 */
function setStateUnsaved() {
	$("#save-status").html("Unsaved");
	$("#save-status").css( "color", "red" );
}

function setStateSaving() {
	$("#save-status").html('Saving <img style="margin-top: -2px;" src="img/loading_icon.gif" alt="...">');
	$("#save-status").css( "color", "green");
}

function setStateSaved() {
	$("#save-status").html("Saved");
	$("#save-status").css( "color", "gray" );
}
