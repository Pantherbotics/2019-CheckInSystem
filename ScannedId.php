<?php

if (!isset($_GET["psswd"])) {
    die('{"error":"No password was sent"}');
}
if (!isset($_GET["id"])) {
    die('{"error":"No id was sent"}');
}
$sentPsswd = $_GET["psswd"];
$sentId = $_GET["id"];

if ($sentPsswd !== "nphs3863"){
    die('{"error":"Incorrect password"}');
}
if (strlen($sentId)!==6 || !Is_Numeric($sentId)) {
    die('{"error":"Invalid id"}');
}    

$dbLink = mysqli_connect("localhost", "PHPACCESS_write", 'M@m,~Q)7u"3Kpsdf'); //host, username, password
//if connection error, die with errno
if(!$dbLink){die('{"error":"Server Error 1-'.mysqli_connect_errno().'"}');}
mysqli_select_db($dbLink, "3863"); //link, schema
//if schema selection error, return errno
if(!$dbLink){die('{"error":"Server Error 2-'.mysqli_errno($dbLink).'"}');}

$sql = '
SELECT
    *
FROM
    Users
WHERE
    id = "'.mysqli_real_escape_string($dbLink, $sentId).'"
;';
$result = mysqli_query($dbLink, $sql);
$rowcount = mysqli_num_rows($result); // number of database rows returned

while ($row = mysqli_fetch_assoc($result)) { //loop through returned rows as arrays
    if (isset($row["Name"])){ //if name and id are stored
        $Return->Name = $row["Name"];
    }else{ // if id is stored but no name attached
        $Return->Name = "Unknown";
    }
}

if ($rowcount == 0){
    $sql = '
    INSERT INTO
        Users
        (id)
    VALUES
        ("'.mysqli_real_escape_string($dbLink, $sentId).'")
    ;';
    mysqli_query($dbLink, $sql);
    if(mysqli_errno($dbLink)!==0){die('{"error":"Server Error 3-'.mysqli_errno($dbLink).'"}');}
    $Return->Name = "Unknown";
}

$sql = '
SELECT
    *
FROM
    Sessions
WHERE
    UserId = "'.mysqli_real_escape_string($dbLink, $sentId).'"
    AND
    TimeOut IS NULL
;';
$result = mysqli_query($dbLink, $sql);
$rowcount = mysqli_num_rows($result); // number of database rows returned

$CurSession = NULL;

while ($row = mysqli_fetch_assoc($result)) { //loop through returned rows as arrays
    $CurSession = $row["SessionId"];
}
if ($CurSession == NULL){ //if timing in  
    $sql = '
    INSERT INTO
        Sessions
        (UserId, TimeIn)
    VALUES
        ("'.mysqli_real_escape_string($dbLink, $sentId).'", CURRENT_TIMESTAMP)
    ;';
    mysqli_query($dbLink, $sql);
    if(mysqli_errno($dbLink)!==0){die('{"error":"Server Error 4-'.mysqli_errno($dbLink).'"}');}
    $Return->isPresent = True;
}else{
    $sql = '
    UPDATE
        Sessions
    SET
        TimeOut = CURRENT_TIMESTAMP
    WHERE
        SessionId = '.$CurSession.'
    ;';
    mysqli_query($dbLink, $sql);
    if(mysqli_errno($dbLink)!==0){die('{"error":"Server Error 5-'.mysqli_errno($dbLink).'"}');}
    $Return->isPresent = False;
}





$Return->id = $sentId;
$Return->error = 0;

$myJSON = json_encode($Return);

echo $myJSON;
?>