<?php
// BlueOffice Breach - ID Badge Photo Upload (port 4500)
//
// Intentionally vulnerable: the extension "whitelist" only checks
// whether an allowed extension appears ANYWHERE in the filename
// (stripos), not that it is the actual final extension. A filename
// like "shell.jpg.php" satisfies the check (it contains ".jpg") while
// Apache still executes it as PHP because ".php" is the real, final
// extension.

if ($_SERVER['REQUEST_METHOD'] !== 'POST' || !isset($_FILES['photo'])) {
    header('Location: /');
    exit;
}

$filename = basename($_FILES['photo']['name']);
$allowed = ['.jpg', '.jpeg', '.png'];

$valid = false;
foreach ($allowed as $ext) {
    if (stripos($filename, $ext) !== false) {
        $valid = true;
        break;
    }
}

if (!$valid) {
    echo "Only JPG or PNG files are allowed.";
    exit;
}

$dest = '/var/www/html/uploads/' . $filename;
move_uploaded_file($_FILES['photo']['tmp_name'], $dest);

echo "Upload successful: <a href=\"/uploads/" . htmlspecialchars($filename) . "\">"
    . htmlspecialchars($filename) . "</a>";
