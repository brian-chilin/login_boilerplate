<?php
// Read the whole file into a string

$config = [];
foreach ([
    "db/host",
    "db/port",
    "db/name",
    "db/user",
    "db/password",
    "html/html_template",
] as $file) {
    $config[$file] = file_get_contents("/etc/config/" . $file);
    if($config[$file] === false) {
        http_response_code(500);
        echo "Failed to read file!";
        exit(1);
    }
}

$options = [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_PERSISTENT => true, // enables persistent connection
];

try {
    $start_time = microtime(true);
    $mustache_replacements = [
        "{{CURRENT_TIME}}" => date('Y-m-d H:i:s'),
        "{{& TABLE_CONTENTS}}" => "",       #
        "{{FORM_USERNAME_VALUE}}" => "",    #
        "{{REQUEST_RESULT}}" => "",         #
        "{{& STATUS}}" => "PHP",
    ];
    
    $dsn = "pgsql:host={$config['db/host']};port={$config['db/port']};dbname={$config['db/name']}";
    $pdo = new PDO($dsn, $config['db/user'], $config['db/password'], $options);
    $stmt_select_by_username = $pdo->prepare("SELECT id, username, password FROM users WHERE username=(:username);");
    $html_template = $config["html/html_template"];

    $stmt = $pdo->query("SELECT * FROM users ORDER BY id;");
    $table = "";
    foreach($stmt->fetchAll(PDO::FETCH_NUM) as $row) {
        #echo var_dump($row);
        $table .= "<tr>";
        foreach($row as $element) {
                $table .= (
                    "<td>" .
                    ($element ?? "NULL") .
                    "</td>"
                );
        }
        $table .= "</tr>";
    }
    $mustache_replacements["{{& TABLE_CONTENTS}}"] = $table;
    $mustache_replacements["{{& STATUS}}"] = microtime(true) - $start_time . "s from PHP";
    
    if (!empty($_POST)) {
        $mustache_replacements["{{FORM_USERNAME_VALUE}}"] = $_POST["username"] ?? "";
        $stmt_select_by_username->execute([
            ':username' => $_POST["username"],
        ]);
        $stmt_result = $stmt_select_by_username->fetch(PDO::FETCH_NUM);
        $mustache_replacements["{{REQUEST_RESULT}}"] = "❌ Invalid Credentials";
        if($stmt_result) {
            #echo var_dump($stmt_result); #debug
            if (password_verify($_POST["password"], $stmt_result[2])) {
                $mustache_replacements["{{REQUEST_RESULT}}"] = "✅ Credentials Verified";
            }
        }

    }

    $html = strtr($html_template, $mustache_replacements);
    echo $html;
} catch (PDOException $e) {
    error_log("DB connection failed: " . $e->getMessage());
    http_response_code(500);
    echo "Server Error 6510<br>" . $j;
    exit(1);
}

?>