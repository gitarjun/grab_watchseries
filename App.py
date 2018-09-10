from flask import Flask,render_template,request
import multiprocessing.dummy as mp
import grablink

app = Flask(__name__)

def _pool_get_gorilla_vid(task):
    name, link, obj = task
    file_name = "{} Season {} Episode {} - {}.mp4".format(*name.split('>'))
    dllink = obj.get_gorilla_vid(link)
    try:
        dllink = '/'.join(dllink.split('/')[:-1])+'/'+file_name
    except AttributeError: # Fails to get download link returns None
        pass
    return {'file_name':file_name,'download_link':dllink}

@app.route("/download", methods=['GET','POST'])
def download():
    if request.method == "POST":
        link = request.form['link']
        try:
            obj = grablink.LinkGrab()
        except:
            return render_template('download.html')
        links = obj.getlinks(link)
        tp=mp.Pool(35)
        to_html = tp.map(_pool_get_gorilla_vid,[(k,v,obj) for k,v in links.items()])
        tp.close()
        tp.join()
        return render_template('download.html', to_html=to_html)
    
    return render_template('download.html')



if __name__=='__main__':
    app.run(debug=True,threaded=True)
