<?php
$curl = curl_init();

$client_id = 'QzBgYS5DLGWCvnS5M3lXNoYoBVvPUVHJ';
$client_secret = 'sfIqeFcSvjfAQBqN';
$redirect_uri= "http://localhost/callback.php";
$authorization_code = $_GET['code'];

curl_setopt_array($curl, array(
CURLOPT_URL => "https://api.dexcom.com/v2/oauth2/token",
CURLOPT_RETURNTRANSFER => true, 
CURLOPT_ENCODING => "",
CURLOPT_MAXREDIRS => 10, 
CURLOPT_TIMEOUT => 30, 
CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1, 
CURLOPT_CUSTOMREQUEST => "POST", 
CURLOPT_POSTFIELDS => "client_secret=$client_secret&client_id=$client_id&code=$authorization_code&grant_type=authorization_code&redirect_uri=$redirect_uri", 
CURLOPT_HTTPHEADER => array( "cache-control: no-cache", "content-type: application/x-www-form-urlencoded" ), 
)); 
$response = curl_exec($curl); 
$err = curl_error($curl); 
curl_close($curl); 
if ($err) { 
echo "cURL Error #:" . $err; 
} 
else
{
$access = substr($response, 17, -93);
$refresh = substr($response, 1250, -2);
echo ($access . "     " . $refresh);
} ?>
