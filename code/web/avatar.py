# -*- coding: utf-8 -*-
__author__ = 'Administrator'
import os
import time

class AvatarUploader:
    def __init__(self):
        self.root_url = ''
        self.folder = 'web/static/avatar'

    def load_url(self, request):
        self.root_url = request.url_root

    def avatar_folder(self):
        return self.root_url+self.folder + time.strftime('%Y-%m-%d')

    def get_lists(self, real_path, request):
        self.load_url(request)
        print self.avatar_folder()
        pathDir =  os.listdir(real_path)
        html = ''
        for allDir in pathDir:
            # child = os.path.join('%s%s' % (REAL_PATH, allDir))
            html +='<li><a href="'+self.avatar_folder()+'/'+allDir+'">'+self.avatar_folder()+'/'+allDir+'</a></li>'
        return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form action="" method=post enctype=multipart/form-data>
          <p><input type=file name=file>
          <input type=text name=uid placeholder=uid>
          <input type=text name=device_id placeholder=device_id>
             <input type=submit value=Upload>
        </form>
        <ol>
        %s
        </ol>
        ''' % html