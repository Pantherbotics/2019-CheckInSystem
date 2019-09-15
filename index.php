<html>
<head>
    <title>3863 | Attendance</title>
    <link rel="stylesheet" href="./css/style.css">
    <link href="https://fonts.googleapis.com/css?family=Open+Sans&display=swap" rel="stylesheet">
</head>

<body>
    <?php
    if (isset($_GET["psswd"])){
        if ($_GET["psswd"]=="nphs3863"){
            echo '
            <p>
            TODO: list attendance records
            <br>
            <a href='.'><button>back</button></a>
            </p><br>
            <image src="/img/Capture.PNG"></img>';
        }else{
            echo '
            <div id="loginFormContainer">
            incorrect password<br>
            <form action="index.php">
                <input type="text" name = "psswd" placeholder="password"></input>
                <button type="Submit">Login</button>
            </form>
            </div>
            ';
        }
    }else{
        echo '
        <div id="loginFormContainer">
        <form action="index.php">
            <input type="text" name = "psswd" placeholder="password"></input>
            <button type="Submit">Login</button>
        </form>
        </div>
        ';
    }
    ?>
</body>
</html>