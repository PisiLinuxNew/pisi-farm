<?php

$r = file_get_contents('php://input');

date_default_timezone_set("Europe/Istanbul");
$dt = date('YmdHis');

$fname = $dt.".txt";
$f = fopen('push/'.$fname,"w");
fwrite($f, $r);
fclose($f);

exec("python /usr/local/bin/github.py /var/www/html/push/ /var/www/html/push.html")
?>
