# -*- coding: utf-8 -*-
__author__ = 'Administrator'

# import Flask Script object
from flask_script import Manager, Server
import sys,os
sys.path.append(os.path.dirname(__file__) + os.sep + '..'+ os.sep)
import main


# Init manager object via app object
manager = Manager(main.app)

# Create a new commands: server
# This command will be run the Flask development_env server

manager.add_command("server", Server(host=main.DevConfig.HOST,port=main.DevConfig.PORT,use_debugger=main.DevConfig.DEBUG))

@manager.shell
def make_shell_context():
    """Create a python CLI.

    return: Default import object
    type: `Dict`
    """
    # 确保有导入 Flask app object，否则启动的 CLI 上下文中仍然没有 app 对象
    return dict(app=main.app)

if __name__ == '__main__':
    manager.run()