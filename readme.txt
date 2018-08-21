
测试用例：20180610
密码：123456

注册：
	用户名：由字母数字下划线组成，不能以下划线开头
	年龄：不能大于100岁
	电话：电话号码:支持13\14\15\18开头的:11位电话
	密码：密码由6位任意字符构成
	
程序命令：
	上传文件:1 下载文件:2 文件管理:3
	文件管理(目前只针对Windows)：
		创建目录:mkdir filename
		    例子：mkdir 123
		修改文件或目录名：rename oldfilename newfilename
		    rename 1234 456
		切换文件目录：cd filename
		    例子：cd 20180610\123

	程序自动展示当前目录：所以不需要lsm命令
	
实现功能模块：登录、注册、文件管理，文件上传，文件下载,断点续传，进度条显示(当文件比较大时比较明显)

服务端：
    注册用户的目录、文件上传下载目录：D:\pythonStudy12\FTPHomework\ftp_server\download\
    断点续传保存目录：D:\pythonStudy12\FTPHomework\ftp_server\breakpoint_resume
客户端：
    文件下载目录：D:\pythonStudy12\FTPHomework\ftp_client\download
    断点续传保存目录：D:\pythonStudy12\FTPHomework\ftp_client\breakpoint_resume


自我感觉：代码混乱













