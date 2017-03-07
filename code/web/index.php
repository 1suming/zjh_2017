<?php
require 'vendor/autoload.php';

// Using Medoo namespace
use Medoo\Medoo;

// Initialize
$database = new Medoo([
    'database_type' => 'mysql',
    'database_name' => 'game',
    'server' => '121.201.29.89',
    'username' => 'root',
    'password' => 'Wgc@db123',
    'charset' => 'utf8',
	'port'   => 23306
]);

