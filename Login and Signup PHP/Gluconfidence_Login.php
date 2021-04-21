<?php

	require_once 'Database_Operation.php';

	$response = array();

	if ($_SERVER['REQUEST_METHOD'] == 'POST') 
	{

    		if (isset($_POST['Username']) && isset($_POST['Password'])) 
		{
        		$db = new DbOperation();
			if ($db->userLogin($_POST['Username'], $_POST['Password'])) 
			{
            			$response['error'] = false;
            			$response['user'] = $db->getUserByUsername($_POST['Username']);
        		} 

			else 
			{
            			$response['error'] = true;
            			$response['message'] = 'Invalid username or password';
        		}

    		} 

		else 
		{
        		$response['error'] = true;
        		$response['message'] = 'Parameters are missing';
    		}

	} 

	else 
	{
    		$response['error'] = true;
    		$response['message'] = "Request not allowed";
	}

	echo json_encode($response);