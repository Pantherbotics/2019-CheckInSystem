<?php

if (!isset($_GET["psswd"])) {
    die('{"error":"No password was sent"}');
}
$sentPsswd = $_GET["psswd"];
if ($sentPsswd !== "nphs3863"){
    die('{"error":"Incorrect password"}');
}


function getNameFromUID($uid){
    $dbLink = mysqli_connect("localhost", "PHPACCESS_write", 'M@m,~Q)7u"3Kpsdf'); //host, username, password
    //if connection error, die with errno
    if(!$dbLink){return "E1_Unknown";}
    mysqli_select_db($dbLink, "3863"); //link, schema
    //if schema selection error, return errno
    if(!$dbLink){return "E2_Unknown";}
    
    $sql = '
    SELECT
        *
    FROM
        Users
    WHERE
        id = "'.$uid.'"
    ;';
    $result = mysqli_query($dbLink, $sql);
    if(mysqli_errno($dbLink)!==0){return "E3_Unknown";}
    
    while ($row = mysqli_fetch_assoc($result)) { //loop through returned rows as arrays
        if (!isset($row["Name"])){
            return "Unknown";
        }
        return $row["Name"];
    }
    return "invalid user";
}


$dbLink = mysqli_connect("localhost", "PHPACCESS_write", 'M@m,~Q)7u"3Kpsdf'); //host, username, password
//if connection error, die with errno
if(!$dbLink){die('{"error":"Server Error 1-'.mysqli_connect_errno().'"}');}
mysqli_select_db($dbLink, "3863"); //link, schema
//if schema selection error, return errno
if(!$dbLink){die('{"error":"Server Error 2-'.mysqli_errno($dbLink).'"}');}



function getTimeElapsedSince($time){
    $dbLink = mysqli_connect("localhost", "PHPACCESS_write", 'M@m,~Q)7u"3Kpsdf'); //host, username, password
    //if connection error, die with errno
    if(!$dbLink){return -9999999;}
    mysqli_select_db($dbLink, "3863"); //link, schema
    //if schema selection error, return errno
    if(!$dbLink){return -9999999;}
    
    $sql = '
    SELECT 
        TIMEDIFF(CURRENT_TIMESTAMP, "'.$time.'")
    ;';
    
    $result = mysqli_query($dbLink, $sql);
    if(mysqli_errno($dbLink)!==0){return -9999999;}
    
    while ($row = mysqli_fetch_assoc($result)) { //loop through returned rows as arrays
        $strhhmmss = reset($row);
        return $strhhmmss;
    }
    return -9999999;
    
}

$sql = '
SELECT
	*
FROM 
	Sessions
WHERE
	TimeOut IS NULL
;';
$result = mysqli_query($dbLink, $sql);
if(mysqli_errno($dbLink)!==0){die('{"error":"Server Error 3-'.mysqli_errno($dbLink).'"}');}

$return;

while ($row = mysqli_fetch_assoc($result)) { //loop through returned rows as arrays
    $sessionInfo = NULL; //clear variable for resuse
    $sessionInfo->name = getNameFromUID($row["UserId"]);
    $sessionInfo->elapsedTime = getTimeElapsedSince($row["TimeIn"]);
    $i = "id-".$row["UserId"];
    $return->$i = $sessionInfo;
}
if (!$return){//if no one logged in
    die('{"error":0,"result":{}}'); 
}

die('{"error":0,"result":'.json_encode($return).'}');
?>