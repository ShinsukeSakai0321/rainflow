#参照先
# https://qiita.com/Gen6/items/2979b84797c702c858b1
import pandas as pd
import Hloop as hloop
import os
import csv
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from werkzeug.utils import secure_filename
app = Flask(__name__,static_folder='outputs')

UPLOAD_FOLDER = './uploads'
RESULTS_FOLDER='./results'
ALLOWED_EXTENSIONS = set(['csv'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER']=RESULTS_FOLDER
app.config['SECRET_KEY'] = os.urandom(24)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('csv.html')


@app.route('/show_csv', methods=['GET', 'POST'])
def show_csv():
    if request.method == 'POST':
        
        
        send_data = request.files['send_data']
        if send_data and allowed_file(send_data.filename):
            filename = secure_filename(send_data.filename)
            send_data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            f = open('uploads/' + filename, 'r', encoding="utf-8")
            f_reader = csv.reader(f)
            ww = list(f_reader)
            # 何故かwwの先頭行のみ、頭に'\ufeff'が付加されてしまう。そこで、二行目からデータが
            #　書かれているものとして読み込むよう下記の処置をすることとした
            wave=[]
            ii=0
            for co in zip(ww):
                ii+=1
                if ii!=1:
                    wave.append(float(co[0][0]))            
            
            hl=hloop.HL()
            name = request.form.get('radio')
            print(name)
            if name=='Wave':
                hl.SetWave(wave)
                hl.Calc()
                halfR,halfM=hl.GetRes()
                peak=hl.GetPeak()
            else:
                hl.SetPeak(wave)
                halfR,halfM=hl.hloop()
            dd=pd.DataFrame({'halfR':halfR,'halfM':halfM})
            dd.to_csv('results/results.csv',index=False)
            if name=='peak':
                dpeak=pd.DataFrame({'peak':peak})
                dpeak.to_csv('results/peak.csv',index=False)
            return render_template('csv.html', result='計算が終了しました。結果をダウンロードして下さい。',name=name)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/results",methods=['GET','POST'])
def results():
    if request.method == 'POST':
        # 現在のディレクトリを取得
        path = os.path.abspath(__file__)[:-7]
        if request.form['action']=='半波+平均':
            return send_from_directory(
                app.config['RESULTS_FOLDER'],
                'results.csv',
                as_attachment=True,
             
                attachment_filename='results.csv',
            )
        if request.form['action']=='ピーク値':
            return send_from_directory(
                app.config['RESULTS_FOLDER'],
                'peak.csv',
                as_attachment=True,
                attachment_filename='peak.csv',
            )
@app.route("/sample",methods=['GET','POST'])
def sample():
    if request.method == 'POST':
        # 現在のディレクトリを取得
        path = os.path.abspath(__file__)[:-7]
        if request.form['action']=='サンプルデータ':
            return send_from_directory(
                directory=app.config['RESULTS_FOLDER'],
                path='wave.csv',
                as_attachment=True,
                attachment_filename='wave.csv',
            )


if __name__ == '__main__':
    app.debug = True
    app.run()