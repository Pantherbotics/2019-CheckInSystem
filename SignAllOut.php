<?php

if (!isset($_GET["psswd"])) {
    die('{"error":"No password was sent"}');
}
$sentPsswd = $_GET["psswd"];
if ($sentPsswd !== "nphs3863"){
    die('{"error":"Incorrect password"}');
}


$dbLink = mysqli_connect("localhost", "PHPACCESS_write", 'M@m,~Q)7u"3Kpsdf'); //host, username, password
//if connection error, die with errno
if(!$dbLink){die('{"error":"Server Error 1-'.mysqli_connect_errno().'"}');}
mysqli_select_db($dbLink, "3863"); //link, schema
//if schema selection error, return errno
if(!$dbLink){die('{"error":"Server Error 2-'.mysqli_errno($dbLink).'"}');}


$sql = '
UPDATE
	Sessions
SET
	ForcedTimeOut = 1
    ,
    TimeOut = CURRENT_TIMESTAMP
WHERE
	TimeOut IS NULL
;';
mysqli_query($dbLink, $sql);
$rowcount = mysqli_affected_rows($dbLink); // number of database rows returned

if(mysqli_errno($dbLink)!==0){die('{"error":"Server Error 3-'.mysqli_errno($dbLink).'"}');}


die('{"error":0,"affectedPeopleCount":'.$rowcount.'}');
?>