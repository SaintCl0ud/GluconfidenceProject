<?php

class DbOperation
{
	private $conn;

	//Constructor
    	function __construct()
    	{
        	require_once dirname(__FILE__) . '/Env_Vars.php';
        	require_once dirname(__FILE__) . '/Database_Connector.php';
        	// opening db connection
        	$db = new DbConnect();
        	$this->conn = $db->connect();
    	}

	//Function used for user login
	public function userLogin($username, $pass)
	{
		//Getting password from database
		$password_in_db = $this->conn->prepare("SELECT Password FROM UserAccount WHERE Username = ?");
		$password_in_db->bind_param("s", $username);
		$password_in_db->execute();
		$password_in_db->store_result();
		$password_in_db->bind_result($password_from_db);
		$password_in_db->fetch();

		//If the entered password matches with password in database
		if(password_verify($pass, $password_from_db))
		{
       			$stmt = $this->conn->prepare("SELECT UserID FROM UserAccount WHERE Username = ?");
        		$stmt->bind_param("s", $username);
        		$stmt->execute();
        		$stmt->store_result();
        		return $stmt->num_rows > 0;
		}

		else
		{
			return false;
		}
    	}

	public function getUserByUsername($username)
    	{
        	$stmt = $this->conn->prepare("SELECT UserID, Username, Email, FirstName, Weight, Subscription, Current_GC_Bottles FROM UserAccount WHERE Username = ?");
        	$stmt->bind_param("s", $username);
        	$stmt->execute();
        	$stmt->bind_result($id, $uname, $email, $firstname, $weight, $subscription, $current_gc_bottles);
        	$stmt->fetch();
        	$user = array();
        	$user['UserID'] = $id;
        	$user['Username'] = $uname;
        	$user['Email'] = $email;
        	$user['FirstName'] = $firstname;
		$user['Weight'] = $weight;
		$user['Subscription'] = $subscription;
		$user['Current_GC_Bottles'] = $current_gc_bottles;
        	return $user;
    	}

    	//Function to create a new user
    	public function createUser($username, $pass, $email, $firstname, $lastname, $zipcode, $weight, $age, $gender, $years_with_diabetes, $diabetes_type, $on_insulin, $subscription, $current_gc_bottles, $on_oral_med, $daily_injections_num, $avg_daily_insulin, $activity_level, $join_gc_chat_group)
    	{
		//If there is no user in database with this username or email, then create one
        	if (!$this->isUserExist($username, $email)) 
		{
			//hashing password
      			$password = password_hash($pass, PASSWORD_DEFAULT);
            		$stmt = $this->conn->prepare("INSERT INTO UserAccount (Username, Password, Email, FirstName, LastName, Zip_Code, Weight, Age, Gender, Years_With_Diabetes, Diabetes_Type, On_Insulin, Subscription, Current_GC_Bottles, On_Oral_Medication, Daily_Injections, Avg_Daily_Units_of_Insulin, Activity_Level, Join_GC_Chat_Group) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");
            		$stmt->bind_param("sssssssssssssssssss", $username, $password, $email, $firstname, $lastname, $zipcode, $weight, $age, $gender, $years_with_diabetes, $diabetes_type, $on_insulin, $subscription, $current_gc_bottles, $on_oral_med, $daily_injections_num, $avg_daily_insulin, $activity_level, $join_gc_chat_group);
            		
			if ($stmt->execute()) 
			{
                		return USER_CREATED;
            		} 
		
			else 
			{
                		return USER_NOT_CREATED;
            		}
		} 
	
		else 
		{
            		return USER_ALREADY_EXIST;
        	}
    	}


    	private function isUserExist($username, $email)
    	{
        	$stmt = $this->conn->prepare("SELECT UserID FROM UserAccount WHERE Username = ? OR Email = ?");
        	$stmt->bind_param("ss", $username, $email);
        	$stmt->execute();
        	$stmt->store_result();
        	return $stmt->num_rows > 0;
    	}
}