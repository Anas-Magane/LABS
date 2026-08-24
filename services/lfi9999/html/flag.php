<?php
// BlueOffice Breach - Challenge 8: LFI (port 9999)
//
// Intentionally vulnerable: the "file" parameter is passed straight
// into include() with no sanitization, no whitelist, and no
// open_basedir restriction -> classic Local File Inclusion. This page
// renders nothing when no file is requested, by design.

if (isset($_GET['file'])) {
    $file = $_GET['file'];
    include($file);
}
