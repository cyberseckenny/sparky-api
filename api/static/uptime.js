const os = require('os');

var ut_sec = os.uptime();
var ut_min = ut_sec / 60;
var ut_hour = ut_min / 60;

ut_sec = Math.floor(ut_sec);
ut_min = Math.floor(ut_min);
ut_hour = Math.floor(ut_hour);
ut_hour = ut_hour % 60;
ut_min = ut_min % 60;
ut_sec = ut_sec % 60;
var uptime = "Uptime: "
            + ut_hour + " hours, "
            + ut_min + " minutes, "
            + ut_sec + " seconds ");

document.getElementById("uptime").innerHTML = uptime;

