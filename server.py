import yt_dlp
from flask import Flask, Response,redirect,request,make_response
import requests
import sqlite3
import json,time,datetime, pytz

app = Flask(__name__)

@app.route('/')
def channels():
    return  app.send_static_file('index.html')

@app.route('/external_links')
def channels_ext():
    return  app.send_static_file('externallinks.html')

def get_best_video_url(video_url):
    ydl_opts = {
        'format': 'bv*+ba/b',
        'youtube_include_dash_manifest': False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        formats = info_dict.get('formats', [])
        formats_with_audio = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') != 'none']
        best_video_format = max(formats_with_audio, key=lambda x: x.get('width', 0))
        best_video_url = best_video_format.get('url')
        return best_video_url

@app.route('/stream/channel', methods=['GET'])
def stream():
    # Fetch the YouTube video's URL
    channel_id = request.args['id']
    channel = find_channel(channel_id)
    url = ''
    if channel is None:
        raise ValueError('Channel not found')
    else:
        if channel['manifest_url'] is not None and int(channel['expiry']) > round(time.time()):
            url = channel['manifest_url']
        else:
            youtube_url = channel['src_url']
            url = get_best_video_url(youtube_url)
            print(url)
            expiryArr = url.split('/')
            print(expiryArr)
            ind = expiryArr.index('expire')
            expiry = expiryArr[ind+1]
            print(expiry)
            save_url(channel_id,url,expiry)
    response = requests.get(url, stream=True)

    def generate():
        for chunk in response.iter_content(chunk_size=8192):
            yield chunk

    return Response(generate(), content_type=response.headers['content-type'])

@app.route('/initialize/<scriptname>')
def initialize_system(scriptname):
    connection = get_db_connection()
    with open(scriptname) as f:
        connection.executescript(f.read())
    connection.commit()
    connection.close()
    return  redirect("/", code=302)



@app.route('/add_channel', methods=['POST'])
def add_channel():
    if request.method == 'POST':
        print(request.form['channel_name'])
        if len(find_channel_by_name(request.form['channel_name'])) > 0 :
            return {"message":"Channel already exists"}
        else:
            add_channel(request.form['channel_name'],request.form['src_url'],request.form['grp_type'],request.form['is_youtube'],request.form['img_url'],request.form['tvg_id'])
        return {"message":"Channel Added Sucessfully"} 

@app.route('/update_channel', methods=['POST'])
def update_channel():
    if request.method == 'POST':
        print(request.form['channel_name'])
        update_channel_db(request.form['id'],request.form['channel_name'],request.form['src_url'],request.form['grp_type'],request.form['is_youtube'],request.form['img_url'],request.form['tvg_id'])
        return {"message":"Channel Added Sucessfully"} 

@app.route('/channels', methods=['GET'])
def get_channels():
    if request.method == 'GET':
        rows = find_All_channels()
        data_json = []
        for row in rows:
            expiry = 'Not Available'
            if row['expiry'] != '0':
                expiry = datetime.datetime.fromtimestamp( int(row['expiry'])).astimezone(pytz.timezone('Asia/Kolkata')),
            data = {
                'id':row['id'],
                'title':row['title'],
                'src_url':row['src_url'],
                'manifest_url':row['manifest_url'],
                'expiry':expiry,
                'group_type':row['group_type'],
                'is_youtube':row['is_youtube'],
                'tvg_img':row['tvg_img'],
                'tvg_id':row['tvg_id']
            }
            data_json.append(data)
        return data_json
    
@app.route('/add_external_links', methods=['POST'])
def add_external_m3u_link():
    if request.method == 'POST':
        add_ext_m3u_link(request.form['source_name'],request.form['x_tvg_url'],request.form['m3u_text'])
        return {"message":"Link Added Sucessfully"} 

@app.route('/external_links_info', methods=['GET'])
def get_external_links_info():
    if request.method == 'GET':
        rows = find_All_external_links()
        data_json = []
        for row in rows:
            data = {
                'id':row['id'],
                'source_name':row['source_name'],
                'x_tvg_url':row['x_tvg_url'],
                'm3u_text':row['m3u_text']
            }
            data_json.append(data)
        return data_json

@app.route('/update_external_links', methods=['POST'])
def update_external_links():
    if request.method == 'POST':
        print(request.form['source_name'])
        update_extenal_m3u_db(request.form['id'],request.form['source_name'],request.form['x_tvg_url'],request.form['m3u_text'])
        return {"message":"Channel Added Sucessfully"} 

@app.route('/all_channels.m3u', methods=['GET'])
def get_playlist():
    if request.method == 'GET':
        rows = find_All_channels()
        print(request.host_url)
        data_json = []
        for row in rows:
            expiry = 'Not Available'
            if row['expiry'] != '0':
                expiry = datetime.datetime.fromtimestamp( int(row['expiry'])).astimezone(pytz.timezone('Asia/Kolkata')),
            data = {
                'id':row['id'],
                'title':row['title'],
                'src_url':row['src_url'],
                'manifest_url':row['manifest_url'],
                'expiry':expiry,
                'group_type':row['group_type'],
                'is_youtube':row['is_youtube'],
                'tvg_img':row['tvg_img'],
                'tvg_id':row['tvg_id']
            }
            data_json.append(data)
        
    return generate_m3u_playlist(data_json)

@app.route('/playlist/allchannels.m3u')
def download_file():
    rows = find_All_channels()
    print(request.host_url)
    data_json = []
    for row in rows:
        manifest_url = ''
        expiry = 'Not Available'
        if row['expiry'] != '0':
            expiry = datetime.datetime.fromtimestamp( int(row['expiry'])).astimezone(pytz.timezone('Asia/Kolkata')),
        data = {
            'id':row['id'],
            'title':row['title'],
            'src_url':row['src_url'],
            'manifest_url':row['manifest_url'],
            'expiry':expiry,
            'group_type':row['group_type'],
            'is_youtube':row['is_youtube'],
            'tvg_img':row['tvg_img'],
            'tvg_id':row['tvg_id']
        }
        data_json.append(data)
        
    file_content = generate_m3u_playlist(data_json)

    response = make_response(file_content)
    
    # Set the appropriate headers for the response
    response.headers['Content-Disposition'] = 'attachment; filename=playlist.m3u'
    response.headers['Content-Type'] = 'audio/x-mpegurl'
    
    return response

@app.route('/v2/playlist/allchannels.m3u')
def download_file_v2():
    rows = find_All_channels()
    print(request.host_url)
    data_json = []
    for row in rows:
        manifest_url = ''
        expiry = 'Not Available'
        if row['expiry'] != '0':
            expiry = datetime.datetime.fromtimestamp( int(row['expiry'])).astimezone(pytz.timezone('Asia/Kolkata')),
        data = {
            'id':row['id'],
            'title':row['title'],
            'src_url':row['src_url'],
            'manifest_url':row['manifest_url'],
            'expiry':expiry,
            'group_type':row['group_type'],
            'is_youtube':row['is_youtube'],
            'tvg_img':row['tvg_img'],
            'tvg_id':row['tvg_id']
        }
        data_json.append(data)
    # v2 generation playlist along with external  m3u file or links
    rows_links = find_All_external_links()
    links_data_json = []
    for row in rows_links:
        data = {
            'id':row['id'],
            'source_name':row['source_name'],
            'x_tvg_url':row['x_tvg_url'],
            'm3u_text':row['m3u_text']
        }
        links_data_json.append(data)
        
    file_content = generate_m3u_playlist_v2(data_json,links_data_json)

    response = make_response(file_content)
    
    # Set the appropriate headers for the response
    response.headers['Content-Disposition'] = 'attachment; filename=playlist.m3u'
    response.headers['Content-Type'] = 'audio/x-mpegurl'
    
    return response

@app.route('/channel/<id>', methods=['GET','DELETE'])
def get_channel(id):
    if request.method == 'GET':
        row = find_channel(id)
        data = {
                'id':row['id'],
                'title':row['title'],
                'src_url':row['src_url'],
                'manifest_url':row['manifest_url'],
                'expiry':row['expiry'],
                'group_type':row['group_type'],
                'is_youtube':row['is_youtube'],
                'tvg_img':row['tvg_img'],
                'tvg_id':row['tvg_id'],
            }
        return data
    if request.method == 'DELETE':
        delete_channel(id)
        return 'channel deleted Successfully'

@app.route('/externallinks/<id>', methods=['GET','DELETE'])
def get_external_links(id):
    if request.method == 'GET':
        row = find_external_link(id)
        data = {
                'id':row['id'],
                'source_name':row['source_name'],
                'x_tvg_url':row['x_tvg_url'],
                'm3u_text':row['m3u_text']
            }
        return data
    if request.method == 'DELETE':
        delete_external_link(id)
        return 'channel deleted Successfully'



def get_db_connection():
    conn = sqlite3.connect('database.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

def find_channel_by_name(channel_name):
    conn = get_db_connection()
    channels = conn.execute('SELECT * FROM channels where title="'+channel_name+'"').fetchall()
    conn.close()
    return channels

def find_All_channels():
    conn = get_db_connection()
    channels = conn.execute('SELECT * FROM channels').fetchall()
    conn.close()
    return channels

def find_All_external_links():
    conn = get_db_connection()
    channels = conn.execute('SELECT * FROM ext_raw_m3u').fetchall()
    conn.close()
    return channels

def find_channel(id):
    conn = get_db_connection()
    channel = conn.execute('SELECT * FROM channels where id='+id).fetchone()
    conn.close()
    return channel

def find_external_link(id):
    conn = get_db_connection()
    channel = conn.execute('SELECT * FROM ext_raw_m3u where id='+id).fetchone()
    conn.close()
    return channel

def delete_channel(id):
    conn = get_db_connection()
    channel = conn.execute('DELETE FROM channels where id='+id)
    conn.commit()
    conn.close()
    return channel

def delete_external_link(id):
    conn = get_db_connection()
    channel = conn.execute('DELETE FROM ext_raw_m3u where id='+id)
    conn.commit()
    conn.close()
    return channel

def add_channel(channel_name,src_url,group_type,is_youtube,tvg_img,tvg_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO channels (title, src_url,expiry,group_type,is_youtube,tvg_img,tvg_id) VALUES (?,?,?,?,?,?,?)",
            (channel_name,src_url,'0',group_type,True if is_youtube == 'on' else False,tvg_img,tvg_id)
            )
    conn.commit()
    conn.close()
    return 'done'

def save_url(id,url,expiry):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE channels set expiry = '"+ expiry +"',manifest_url='"+url+"' where id="+id)
    conn.commit()
    conn.close()


def update_channel_db(id,channel_name,src_url,group_type,is_youtube,tvg_img,tvg_id):
    conn = get_db_connection()
    cur = conn.cursor()
    update_template = "UPDATE channels SET expiry = '0', manifest_url = NULL, title = '{channel_name_clm}', src_url = '{src_url_clm}', group_type = '{group_type_clm}', is_youtube = {is_youtube_clm}, tvg_img = '{tvg_img_clm}',tvg_id = '{tvg_id_clm}' WHERE id = {id_clm}"
    update_script = update_template.format(channel_name_clm=channel_name, src_url_clm=src_url, group_type_clm=group_type, is_youtube_clm=True if is_youtube == 'on' else False, tvg_img_clm=tvg_img, tvg_id_clm=tvg_id, id_clm=id)
    #print(update_script)
    cur.execute(update_script)
    conn.commit()
    conn.close()

def add_ext_m3u_link(source_name,x_tvg_url,m3u_text):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO ext_raw_m3u (source_name,x_tvg_url,m3u_text) VALUES (?,?,?)",
            (source_name,x_tvg_url,m3u_text)
            )
    conn.commit()
    conn.close()
    return 'done'

def update_extenal_m3u_db(id,source_name,x_tvg_url,m3u_text):
    conn = get_db_connection()
    cur = conn.cursor()
    update_template = "UPDATE ext_raw_m3u SET source_name = '{source_name_clm}', x_tvg_url = '{x_tvg_url_clm}', m3u_text = '{m3u_text_clm}' WHERE id = {id_clm}"
    update_script = update_template.format(source_name_clm=source_name, x_tvg_url_clm=x_tvg_url, m3u_text_clm=m3u_text, id_clm=id)
    #print(update_script)
    cur.execute(update_script)
    conn.commit()
    conn.close()

def generate_m3u_playlist(channels):
    playlist = '#EXTM3U x-tvg-url="https://www.tsepg.cf/epg.xml.gz"\n'
    print(channels)
    for channel in channels:
        playlist += "#EXTINF:-1 tvg-id=\"{}\" tvg-logo=\"{}\" group-title=\"{}\",{}\n".format(
            channel['tvg_id'], channel['tvg_img'], channel['group_type'], channel['title']
        )
        if channel['is_youtube'] == 1:
            playlist += request.host_url +'stream/channel?id='+str(channel['id'])+ '\n'
        else :
            playlist += channel['src_url']+ '\n'


    return playlist

def generate_m3u_playlist_v2(channels,ext_links):
    if not ext_links:
        playlist = "#EXTM3U\n"
    else :
        playlist = "#EXTM3U "+ext_links[0]['x_tvg_url']+"\n"
    #print(channels)
    # for channel in channels:
    #     playlist += "#EXTINF:-1 tvg-id=\"{}\" tvg-logo=\"{}\" group-title=\"{}\",{}\n".format(
    #         channel['title'], channel['tvg_img'], channel['group_type'], channel['title']
    #     )
    #     if channel['is_youtube'] == 1:
    #         playlist += request.host_url +'stream/channel?id='+str(channel['id'])+ '\n'
    #     else :
    #         playlist += channel['src_url']+ '\n'
    if ext_links:
        playlist += "\n"+ext_links[0]['m3u_text']+"\n"

    return playlist


config = {
    "DEBUG": True,  # run app in debug mode
    "host":"0.0.0.0"
}
app.config.from_mapping(config)
if __name__ == '__main__':
    app.run(host='0.0.0.0')
