<?php



$redis = new Redis();
   $redis->connect('127.0.0.1', 6379);
  // echo "Connection to server sucessfully";
         //查看服务是否运行
  // echo "Server is running: " . $redis->ping();



if(empty($_FILES['file'])){
	goto bk;
}

$file = $_FILES['file'];//得到传输的数据
//得到文件名称
$name = $file['name'];

$name = $_POST['uid'].'_'.$_POST['device_id'].'_'.$name;
$type = strtolower(substr($name,strrpos($name,'.')+1)); //得到文件类型，并且都转化成小写
$allow_type = array('jpg','jpeg','gif','png'); //定义允许上传的类型
//判断文件类型是否被允许上传
if(!in_array($type, $allow_type)){
  //如果不被允许，则直接停止程序运行
  return ;
}
//判断是否是通过HTTP POST上传的
//if(!is_uploaded_file($file['tmp_name'])){
  //如果不是通过HTTP POST上传的
  //return ;
//}
$upload_path = 'C:\Users\Administrator\Desktop\server\code_1122_source\code\web\static\upload\\'; //上传文件的存放路径
//开始移动文件到相应的文件夹
if(move_uploaded_file($file['tmp_name'],$upload_path.$name)){

$con=mysqli_connect("localhost","root","root","game");




// 检测连接
if (mysqli_connect_errno())
{
  echo "连接失败: " . mysqli_connect_error();
}
$sql = "UPDATE `user` SET `avatar` = 'http://192.168.2.75:5000/static/upload/".$name."' WHERE `id`=".$_POST['uid'];



$rs = mysqli_query($con, $sql);

mysqli_close($con);



$redis->hset('u'.$_POST['uid'],'avatar','http://192.168.2.75:5000/static/upload/'.$name);





	echo json_encode([
		'result'=>0,
		'message'=>'success,'.$rs,
		'url'=>'http://192.168.2.75:5000/static/upload/'.$name
	]);
	return;

}else{
  echo json_encode([
  	'result'=>1,
  	'message'=>'error'
  ]);
  return;
}
bk:
?>

<form action="." name="form" method="post" enctype="multipart/form-data">
  <input type=text name=uid placeholder=uid>
  <input type=text name=device_id placeholder=device_id>
  <input type="file" name="file" />
  <input type="submit" name="submit" value="上传" />
</form>

