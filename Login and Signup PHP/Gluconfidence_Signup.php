<?php

//importing required script
require_once 'Database_Operation.php';

$response = array();

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
	if (!verifyRequiredParams(array('Username', 'Password', 'Email', 'FirstName', 'LastName', 'Zip_Code', 'Weight', 'Age', 'Gender', 'Years_With_Diabetes', 'Diabetes_Type', 'On_Insulin', 'Subscription', 'Current_GC_Bottles', 'On_Oral_Medication', 'Daily_Injections', 'Avg_Daily_Units_of_Insulin', 'Activity_Level', 'Join_GC_Chat_Group'))) 
	{
        	//getting values
        	$username = $_POST['Username'];
		echo $username;
        	$password = $_POST['Password'];
        	$email = $_POST['Email'];
        	$firstname = $_POST['FirstName'];
		$lastname = $_POST['LastName'];
		$zip = $_POST['Zip_Code'];
		$weight = $_POST['Weight'];
		$age = $_POST['Age'];
		$gender = $_POST['Gender'];
		$years_with_diabetes = $_POST['Years_With_Diabetes'];
		$diabetes_type = $_POST['Diabetes_Type'];
		$on_insulin = $_POST['On_Insulin'];
		$subscription = $_POST['Subscription'];
		$current_gc_bottles = $_POST['Current_GC_Bottles'];
		$on_oral_meds = $_POST['On_Oral_Medication'];
		$daily_injections = $_POST['Daily_Injections'];
		$avg_daily_units_of_insulin = $_POST['Avg_Daily_Units_of_Insulin'];
		$activity_level = $_POST['Activity_Level'];
		$join_gc_chat_group = $_POST['Join_GC_Chat_Group'];

        	//creating db operation object
        	$db = new DbOperation();

        	//attempting to add user to database
        	$result = $db->createUser($username, $password, $email, $firstname, $lastname, $zip, $weight, $age, $gender, $years_with_diabetes, $diabetes_type, $on_insulin, $subscription, $current_gc_bottles, $on_oral_meds, $daily_injections, $avg_daily_units_of_insulin, $activity_level, $join_gc_chat_group);

        	//making the response accordingly
        	if ($result == USER_CREATED) 
		{
            		$response['error'] = false;
            		$response['message'] = 'User created successfully';
        	} 

		elseif ($result == USER_ALREADY_EXIST) 
		{
            		$response['error'] = true;
            		$response['message'] = 'User already exist';
        	} 

		elseif ($result == USER_NOT_CREATED) 
		{
           	 	$response['error'] = true;
            		$response['message'] = 'Some error occurred';
        	}
    	} 
	
	else 
	{
        	$response['error'] = true;
        	$response['message'] = 'Required parameters are missing';
    	}
} 

else 
{
    $response['error'] = true;
    $response['message'] = 'Invalid request';
}

//function to validate the required parameter in request
function verifyRequiredParams($required_fields)
{

	//Getting the request parameters
    	$request_params = $_REQUEST;

    	//Looping through all the parameters
    	foreach ($required_fields as $field) 
	{
        	//if any requred parameter is missing
        	if (!isset($request_params[$field]) || strlen(trim($request_params[$field])) <= 0) 
		{
            		return true;
        	}
    	}
    
	return false;
}

echo json_encode($response);