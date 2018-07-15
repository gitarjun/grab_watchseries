from flask import Flask,render_template,request
import grablink

app = Flask(__name__)


@app.route("/download", methods=['GET','POST'])
def download():
    if request.method == "POST":
        link = request.form['link']
        try:
            obj = grablink.LinkGrab()
        except:
            return render_template('download.html')
        links = obj.getlinks(link)
        to_html = []
        for name,link in links.items():
            file_name = "{} Season {} Episode {} - {}.mp4".format(*name.split('>'))
            dllink = obj.get_gorilla_vid(link)
            try:
                dllink = '/'.join(dllink.split('/')[:-1])+'/'+file_name
            except AttributeError: # Fails to get download link returns None
                pass
            to_html.append({'file_name':file_name,'download_link':dllink})
        return render_template('download.html', to_html=to_html)
    return render_template('download.html')



if __name__=='__main__':
    app.run(debug=True,threaded=True)