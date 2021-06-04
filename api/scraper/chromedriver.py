import undetected_chromedriver as uc

class Driver:
    def __init__(proxy_host, proxy_port, proxy_user, proxy_password):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy_user = proxy_user
        self.proxy_password = proxy_password
   
    def get_chromedriver():
        path = os.path.dirname(os.path.abspath(__file__))
        chrome_options = uc.ChromeOptions()
    
        # proxy stuff
        plugin_file = 'proxy_auth_plugin.zip'
        with zipfile.ZipFile(pluginfile, 'w') as zip:
            zip.writestr('manifest.json', manifest_json)
            zip.writestr('background.js', background_js)
        chrome_options.add_extension(plugin_file)    

        driver = uc.Chrome(os.path.join(path, 'chromedriver'),
                           chrome_options=chrome_optinos)
        return driver

    
    
