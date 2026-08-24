<?php
// BlueOffice Breach - ID Badge Photo Upload (port 4500)
?>
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>BlueOffice ID Badge Photo Upload</title></head>
<body>
<h1>BlueOffice ID Badge Photo Upload</h1>
<p>Upload your employee ID badge photo. JPG or PNG files only.</p>
<form method="post" action="/upload.php" enctype="multipart/form-data">
  <input type="file" name="photo">
  <button type="submit">Upload</button>
</form>
</body>
</html>
