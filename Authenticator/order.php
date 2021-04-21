<?php
if( isset($_GET['submit']) )
{
    //be sure to validate and clean your variables
    $val1 = htmlentities($_GET['val1']);
    

    //then you can use them in a PHP function. 
	function Order($val1){
        
		$curl = curl_init();

		curl_setopt_array($curl, array(
  		CURLOPT_URL => "https://1fb37288355879e26225b275336261c8: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@gluconfidence.myshopify.com/admin/api/2021-01/orders.json?ids=$val1",
  		CURLOPT_RETURNTRANSFER => true,
  		CURLOPT_ENCODING => "",
  		CURLOPT_MAXREDIRS => 10,
  		CURLOPT_TIMEOUT => 30,
  		CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
  		CURLOPT_HTTPHEADER => array(
    	"cache-control: no-cache",
    	"content-type: application/x-www-form-urlencoded"
  		),
		));

		$response = curl_exec($curl);
		$err = curl_error($curl);

		curl_close($curl);

		if ($response == '{"orders":[]}') {
  			echo "Order Does Not Exist";
		} else {
  		header("Location: http://localhost/index.php");
    	exit;
		}
		
		}
$result = Order($val1);
}
?>

<?php if( isset($result) ) echo $result; //print the result above the form ?>

<form action="" method="get">
    Order Number: 
    <input type="text" name="val1" id="val1"></input>


    <input type="submit" name="submit" value="send"></input>
</form>
