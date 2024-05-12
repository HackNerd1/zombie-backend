var express = require('express');
var router = express.Router();
var multer  = require('multer');
var path = require('path');
var fs = require('fs');
// let jsexecpy = require('jsexecpy');
const { exec } = require('child_process');

/* GET home page. */
function ConvertToTable(data, callBack) {
    data = data.toString();
    var table = new Array();
    var rows = new Array();
    rows = data.split("\n");
    for (var i = 0; i < 6; i++) {
        table.push(rows[i].split(","));
    }
    callBack(table);
}
router.get('/', function(req, res, next) {
    res.send('successful')
});
router.get('/gettable/', function(req, res, next) {
    // fs.readFile('./model/output/output.csv',(error, data  =>{
    //     if (error) {
    //         console.log(error);
    //         res.send([])
    //     }else{
    //         ConvertToTable(data, function (table) {
    //             res.send(table)
    //         })
    //     }
    // }))
    try {
        fs.readFile('/app/model/output/output.csv',( (error,data)  =>{
            if (error) {
                console.log(error);
                res.send([])
            }else{
                ConvertToTable(data, function (table) {
                    res.send(table)
                })
            }
        }))
    } catch (error) {
        
    }

});
router.get('/download/', function(req, res, next) {
    var stream = fs.createReadStream( "/app/model/output/output.csv" );//参数是图片资源路径
    var responseData = [];//存储文件流
    if (stream) {//判断状态
        stream.on( 'data', function( chunk ) {
            responseData.push( chunk );
        });
        stream.on( 'end', function() {
            var finalData = Buffer.concat( responseData );
        res.write( finalData );
        //第一个参数是下载下来要存放的位置，第二个参数是图片数据（二进制的），第三个参数必须要binary，第四个是回调函数
        stream.pipe(res);
        });
    }
});

router.get('/predict/', function(req, res, next) {
    file = exec('python3 /app/model/model.py', (error, stdout, stderr) => {
        if (error) {
          console.error(`执行的错误: ${error}`);
          return;
        }
        console.log(`stdout: ${stdout}`);
        console.error(`stderr: ${stderr}`);
      });
    file.on('exit', function (code, signal) {
        console.log('子进程已退出，代码：' + code);
        res.send('successful');
    });

});


router.get('/plotData/', function(req, res, next) {
    file = exec('python3 /app/model/output/plot_data.py', (error, stdout, stderr) => {
        if (error) {
          console.error(`执行的错误: ${error}`);
          return;
        }
        console.log(`stdout: ${stdout}`);
        console.error(`stderr: ${stderr}`);
      });
    file.on('exit', function (code, signal) {
        console.log('子进程已退出，代码：' + code);
        var file = '/app/model/output/plot_data.json'; //文件路径，__dirname为当前运行js文件的目录

        //读取json文件
        fs.readFile(file, 'utf-8', function(err, data) {
            if (err) {
                res.send('文件读取失败');
            } else {
                res.send(data);
            }
        });
        // res.send('successful');
    });

 

});

 

// 文件上传
var upload = multer({dest: 'upload_tmp/'});

router.post('/uploadcsv/', upload.array('csvfile',4), function(req, res, next) {
    console.log(req.files[0]);  // 上传的文件信息

    var temp_file = req.files[0].path;
    var des_file = "./upload_tmp/" + req.files[0].originalname;

    fs.rename(temp_file, des_file, function (err) {
        if( err ){
            console.log( err );
        }else{
            response = {
                message:'File uploaded successfully',
                filename:req.files[0].originalname
            };
            console.log( response );
            res.end( JSON.stringify( response ) );
        }
    });
});

module.exports = router;
