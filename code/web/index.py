# -*- coding: utf-8 -*-
import os
from flask import Flask, request, redirect, url_for
from gevent import monkey

from werkzeug import secure_filename
from flask import jsonify
import mysql.connector

UPLOAD_FOLDER = 'static/upload'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
monkey.patch_all()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
def get_conn():
    conn = None
    try:
        conn = mysql.connector.connect(host='10.0.1.36',
        user='root',
        password='123456',
        port=3306 ,
        database='game',
        charset='utf8')
    except mysql.connector.Error as e:
        print e.message
    return conn
def execute(conn, sql):
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
    except mysql.connector.Error as e:
        cursor.close()
        conn.close()
        return jsonify(result=-1,message=e.message)
    return True
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        file = request.files['file']
        uid = request.form['uid']
        device_id = request.form['device_id']

        if file == None or uid == None or device_id == None:
            return jsonify(result=0,message='error,file or uid or device_id is empty!')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], uid+'_'+device_id+'_'+filename))
            # return redirect(url_for('uploaded_file', filename=filename))
            full_filename ='/'+uid+'_'+device_id+'_'+filename
            path_url = 'http://192.168.2.75:5000/'+app.config['UPLOAD_FOLDER']+full_filename

            conn = get_conn()
            if conn == False:
                return jsonify(result=-1,message='error:get conn false')
            if execute(conn, "UPDATE `user` SET `avatar` = '%s' WHERE `id`=%d" % (path_url, int(uid))):
                return jsonify(result=0,message='success,message:'+full_filename+',path:'+path_url,url=path_url)
            return jsonify(result=-1,message='error:upload return false')
            #return jsonify(rr=0,mm='success,message:'+full_filename+',path:'+path_url,uu=path_url)

    return '''
    <!doctype html>
    <title>Upload new File</title>

    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
      <input type=text name=uid placeholder=uid>
      <input type=text name=device_id placeholder=device_id>
         <input type=submit value=Upload>
    </form> '''
# ''' % "<br>".join(os.listdir(app.config['UPLOAD_FOLDER'],))
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000,threaded=True,debug=True)