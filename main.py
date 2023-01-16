from flask import Flask,render_template,request
import subprocess
import speedtest
import os

app = Flask(__name__)

@app.route('/',methods=['POST','GET'])
def index():
    current=(subprocess.check_output("netsh wlan show interfaces").decode("utf-8").split("\n"))
    left=[i.split(":")[0][1:-1] for i in current if ":" in i]
    right=[i.split(":")[1][1:-1] for i in current if ":" in i]
    final=list(zip(left,right))
    return render_template("index.html",final=final)

@app.route('/speed')
def speed():
    # import speedtest module 
    speed_test = speedtest.Speedtest()

    download_speed = speed_test.download()
    download_speed= download_speed//(1024*1024)
   

    upload_speed = speed_test.upload()
    upload_speed=upload_speed//(1024*1024)

    return render_template("speed.html",download_speed=download_speed,upload_speed=upload_speed)

@app.route('/saved')
def saved_wifi():
        
    data = (
        subprocess.check_output(["netsh", "wlan", "show", "profiles"])
        .decode("utf-8")
        .split("\n")
    )
    profiles = [i.split(":")[1][1:-1] for i in data if "All User Profile" in i]
    passwd=[]

    for i in range(0,len(profiles)):
        results = (
            subprocess
            .check_output(["netsh", "wlan", "show", "profile", profiles[i], "key=clear"])
            .decode("utf-8")
            .split("\n")
        )
        results = [b.split(":")[1][1:-1] for b in results if "Key Content" in b]

        
        try:
            passwd.append(results[0])


        except IndexError:
             passwd.append(" ")
    my_list=list(zip(profiles,passwd))
  
    return render_template("saved_wifi.html",my_list=my_list)



@app.route('/avail')
def show_available():
    a=(subprocess.check_output(["netsh", "wlan", "show", "network"]).decode("utf-8").split("\n"))
    avail_net=[i.split(":")[1][1:-1] for i in a if "SSID" in i]
    return render_template("avail.html",avail_net=avail_net)    
 


@app.route('/html_connection',methods=['POST','GET'])
def html_connection():
    return render_template("connection.html")

@app.route('/html_connect',methods=['POST','GET'])
def html_connect():
    return render_template("connect.html")

@app.route('/connect',methods=['POST','GET'])
def connect():
    if request.method == 'POST':
        name=request.form['name']
        ssid=request.form['ssid']
        command = "netsh wlan connect name=\""+name+"\" ssid=\""+ssid+"\" interface=Wi-Fi"
        os.system(command)        
    return "action commited"

@app.route('/html_add',methods=['POST','GET'])
def html_add():
    return render_template("add.html")

@app.route('/add',methods=['POST','GET'])
def add_wifi():
    if request.method == 'POST':
        name=request.form['name']
        ssid=request.form['ssid']
        passwd=request.form['passwd']
        config = """<?xml version=\"1.0\"?>
                    <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
                        <name>"""+name+"""</name>
                        <SSIDConfig>
                            <SSID>
                                <name>"""+ssid+"""</name>
                            </SSID>
                        </SSIDConfig>
                        <connectionType>ESS</connectionType>
                        <connectionMode>auto</connectionMode>
                        <MSM>
                            <security>
                                <authEncryption>
                                    <authentication>WPA2PSK</authentication>
                                    <encryption>AES</encryption>
                                    <useOneX>false</useOneX>
                                </authEncryption>
                                <sharedKey>
                                    <keyType>passPhrase</keyType>
                                    <protected>false</protected>
                                    <keyMaterial>"""+passwd+"""</keyMaterial>
                                </sharedKey>
                            </security>
                        </MSM>
                    </WLANProfile>"""
        command = "netsh wlan add profile filename=\""+name+".xml\""+" interface=Wi-Fi"
        with open(name+".xml", 'w') as file:
             file.write(config)
        os.system(command)            

    return "wifi added successfully"

@app.route('/html_delete',methods=['POST','GET'])
def html_delete():
    return render_template("delete.html")  

@app.route('/delete',methods=['POST','GET'])
def delete():
     if request.method == 'POST':
       
        ssid=request.form['ssid']
        command = "netsh wlan delete profile name=\""+ssid+"\" "
        os.system(command)       
     return "profile deleted"





 
# main driver function
if __name__ == '__main__':
    app.run()